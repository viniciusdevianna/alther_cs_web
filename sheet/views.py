import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from sheet.models import *
from sheet.forms import CreateCharForm, AttributeForm, ActionForm

# Authentication functions
def owner_test(user: User, character: Character):
    return user == character.player_ID

def is_ajax(request):
    return request.accepts('application/json') and request.method == 'GET'

# Loading functions
def load_char_data(character: Character) -> dict:
    actions = Action.objects.filter(char_ID=character)
    attributes = Attribute.objects.filter(char_ID=character)
    available_paths = AvailablePath.objects.filter(char_ID=character)
    active_path = available_paths.get(path_ID=character.active_path)
    available_skills = AvailableSkill.objects.filter(char_ID=character)
    equipped_skills = EquippedSkill.objects.get(char_ID=character)

    equipped_skills_dict = load_char_equipped_skills(equipped_skills)
    

    return {
        'character': character,
        'attributes': attributes,
        'available_paths': available_paths,
        'active_path': active_path,
        'available_skills': available_skills,
        'equipped_skills': equipped_skills,
        'equipped_skills_dict': equipped_skills_dict,
        'actions': actions,
    }

def load_char_equipped_skills(skills: EquippedSkill) -> dict:
    equipped_skills_dict = {}
    
    for field in skills.get_slots():
        if field != 'intrinsic':
            equipped_skills_dict[field] = getattr(skills, field)

    return equipped_skills_dict

@login_required
def main(request, char_ID=None):
    if request.method == 'POST':
        char_ID = request.POST.get('character')
    
    if char_ID is None:
        return redirect('pick_character')

    character = Character.objects.get(id=char_ID)
    if not owner_test(request.user, character):
        return redirect('pick_character')

    char_data = load_char_data(character=character)    

    return render(request, 'sheet/main.html', char_data)
    
# Views that manipulate data in the main sheet view
def roll_action(request):
    if not is_ajax(request):
        return redirect('home')
    
    action_ID = int(request.GET.get('action_ID'))
    action_to_roll = Action.objects.get(pk=action_ID)
    roll = action_to_roll.roll_dice()

    response = {
        "roll": roll,
        "action": action_to_roll.type
    }

    return JsonResponse(response)


def level_up(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    new_total_xp = int(request.GET.get('total_XP'))
    character = Character.objects.get(pk=char_ID)
    # char_attrs = Attribute.objects.filter(char_ID=character)
    # char_actions = Action.objects.filter(char_ID=character)

    xp_diff = new_total_xp - character.xp_total
    character.xp_current += xp_diff
    if new_total_xp % 1000 == 0:
        character.level = new_total_xp // 1000 + 1
    #     for _ in range(xp_diff // 1000):
    #         character.hp_total += 10
    #         for attr in char_attrs:
    #             attr.level_up()
    #             attr.save()
    #         for action in char_actions:
    #             action.level_up()
    #             action.save()
    character.xp_total = new_total_xp
    character.save()

    response = {'level': character.level,
                'xp_current': character.xp_current,
                'xp_total': character.xp_total}

    return JsonResponse(response)


def update_basic(request):
    if not is_ajax(request):       
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    info_to_update = request.GET.get('info_to_update')
    new_value = request.GET.get('new_value')

    character = Character.objects.get(pk=char_ID)
    old_value = getattr(character, info_to_update)

    # If the attr to update uses int values, we have to cast the string new_value to int
    # If the attr already uses a string, we can skip this cast
    if type(new_value) != type(old_value):
        new_value = type(old_value)(new_value)

    setattr(character, info_to_update, new_value)
    character.save()

    return JsonResponse({info_to_update: new_value})

def manipulate_attribute(request):
    if not is_ajax(request):
        return redirect('home')
    
    attr_ID = int(request.GET.get('attr_ID'))
    operation = int(request.GET.get('operation'))

    attribute = Attribute.objects.get(pk=attr_ID)

    attribute.current_value += operation
    attribute.save()

    return JsonResponse({'new_value': attribute.current_value})

def change_active_path(request):
    if not is_ajax(request):
        return redirect('home')
    
    new_active_path = int(request.GET.get('active_path'))
    char_ID = int(request.GET.get('char_ID'))

    character = Character.objects.get(pk=char_ID)
    path = AvailablePath.objects.get(pk=new_active_path)
    equipped_skills = EquippedSkill.objects.get(char_ID=character)
    new_intrinsic = Skill.objects.filter(path=path.path_ID).get(_category=Skill.Category.INTRINSIC)

    character.active_path = path.path_ID
    equipped_skills.intrinsic = new_intrinsic
    character.save()
    equipped_skills.save()

    response = {
        'current_pp': path.current_pp,
        'total_pp': path.total_pp,
        'level': path.level,
        'is_master': path.is_master,
        'skill_name': new_intrinsic.name,
        'skill_description': new_intrinsic.description
    }

    return JsonResponse(response)

def update_text(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    info_to_update = request.GET.get('info_to_update')
    new_text = request.GET.get('new_text')

    character = Character.objects.get(pk=char_ID)
    setattr(character, info_to_update, new_text)
    character.save()

    return JsonResponse({'response': 'success'})

def manipulate_pathpoints(request):
    if not is_ajax(request):
        return redirect('home')
    
    active_path_ID = int(request.GET.get('active_path'))
    new_total_pp = int(request.GET.get('new_total_pp'))

    path = AvailablePath.objects.get(pk=active_path_ID)
    path.change_total_pp(new_total_pp)
    path.save()

    response = {
        'current_pp': path.current_pp,
        'total_pp': path.total_pp,
        'level': path.level,
        'is_master': path.is_master
    }

    return JsonResponse(response)

# Views for new sheet creation and editing char information outside of main sheet page
@login_required
def create_character(request):    
    form = CreateCharForm()

    if request.method == 'POST':
        form = CreateCharForm(request.POST)

        if form.is_valid():
            player = request.user
            new_char = Character(player_ID=player)
            new_char.active_path = Path.objects.get(pk='NOV')
            form = CreateCharForm(request.POST, instance=new_char)

            new_char = form.save()

            paths = Path.objects.filter(aspiration=new_char.aspiration, tier=Path.Tier.BASIC)
            for path in paths:
                available_path = AvailablePath(char_ID=new_char, path_ID=path)
                available_path.save()
                
            active_initial_path = AvailablePath.objects.filter(char_ID=new_char).first()
            if active_initial_path is not None:
                new_char.active_path = active_initial_path.path_ID
                new_char.save()        

            intrinsic_skill = Skill.objects.filter(_category=Skill.Category.INTRINSIC).get(path=new_char.active_path)
            equipped_skill = EquippedSkill(char_ID=new_char, intrinsic=intrinsic_skill)
            equipped_skill.save()
            
            for action_type in Action.ActionTypes:
                new_action = Action(type=action_type, char_ID=new_char)
                new_action.save()
            
            return redirect('new_path', char_ID=new_char.pk)

    return render(request, 'sheet/create.html', {'form': form})

@login_required
def update_attributes(request, char_ID):
    character = Character.objects.get(id=char_ID)
    if Attribute.objects.filter(char_ID=char_ID).exists():
        attributes = Attribute.objects.filter(char_ID=char_ID)
        redirect_to = {'to': 'main', 'char_ID': char_ID}
    else:
        attributes = (
            Attribute(char_ID=character, type=this_type) for this_type in Attribute.AttrTypes
        )
        redirect_to = {'to': 'skills', 'char_ID': char_ID}

    if request.method == 'POST':
        forms = tuple(
            AttributeForm(
                request.POST, instance=this_attr, prefix=f'form{form_number}'
            ) for form_number, this_attr in enumerate(attributes) 
        )

        check_forms = (form.is_valid() for form in forms)
        if all(check_forms):
            for form in forms:
                form.save()           
            messages.success(request, 'Atributos atualizados')
            return redirect(**redirect_to)
        else:
            messages.error(request, 'Atributos inválidos')
            return redirect('update_attributes', char_ID=char_ID)
    
    forms = (
        AttributeForm(
            instance=this_attr, prefix=f'form{form_number}'
        ) for form_number, this_attr in enumerate(attributes)
    )

    form_data = {
        'forms': forms,
        'character': character
    }
    
    return render(request, 'sheet/attributes.html', form_data)

@login_required
def new_path(request, char_ID):
    character = Character.objects.get(pk=char_ID)

    if request.method == 'POST':
        path_ID = request.POST.get('path_chosen')
        path = Path.objects.get(pk=path_ID)

        character.active_path = path

        char_path = AvailablePath.objects.filter(char_ID=character).get(path_ID=path)
        char_path.total_pp = 100
        char_path.current_pp = char_path.total_pp

        intrinsic_skill = Skill.objects.filter(_category=Skill.Category.INTRINSIC).get(path=path)
        equipped_skill = EquippedSkill.objects.get(char_ID=character)

        equipped_skill.intrinsic = intrinsic_skill

        character.save()
        char_path.save()
        equipped_skill.save()

        return redirect('update_attributes', char_ID=char_ID)

    available_paths = [path.path_ID for path in AvailablePath.objects.filter(char_ID=char_ID)]
    aspiration_paths = Path.objects.filter(aspiration=character.aspiration)

    paths_data = {
        'character': character,
        'available_paths': available_paths,
        'aspiration_paths': aspiration_paths
    }

    return render(request, 'sheet/newpath.html', paths_data)

@login_required
def update_bg(request, char_ID):
    character = Character.objects.get(pk=char_ID)

    if request.method == 'POST':
        form = CreateCharForm(request.POST, instance=character)
        form.save()

        return redirect('main', char_ID=char_ID)
    
    form = CreateCharForm(instance=character)

    form_data = {
        'form': form,
        'character': character
    }

    return render(request, 'sheet/bg.html', form_data)

@login_required
def update_actions(request, char_ID):
    actions = Action.objects.filter(char_ID=char_ID)    

    if request.method == 'POST':
        forms = tuple(
            ActionForm(
                request.POST, instance=this_action, prefix=f'form{form_number}'
            ) for form_number, this_action in enumerate(actions) 
        )

        check_forms = (form.is_valid() for form in forms)
        if all(check_forms):
            for form in forms:
                form.save()
            messages.success(request, 'Ações atualizadas')
            return redirect('main', char_ID=char_ID)
        else:
            messages.error(request, 'Ações inválidas')
            return redirect('update_actions', char_ID=char_ID)

    character = Character.objects.get(pk=char_ID)
    
    forms = (
        ActionForm(
            instance=this_action, prefix=f'form{form_number}'
        ) for form_number, this_action in enumerate(actions)
    )

    form_data = {
        'forms': forms,
        'character': character
    }

    return render(request, 'sheet/actions.html', form_data)

def evolve(request, char_ID):
    character = Character.objects.get(pk=char_ID)
    actions = Action.objects.filter(char_ID=character)
    attributes = Attribute.objects.filter(char_ID=character)    

    data = {
        'character': character,
        'attributes': attributes,
        'actions': actions
    }

    return render(request, 'sheet/evolve.html', data)

def upgrade_attribute(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    attribute_type = request.GET.get('attribute_type')
    action_to_take = int(request.GET.get('action_to_take'))
    is_training = json.loads(request.GET.get('is_training', 'false'))

    character = Character.objects.get(pk=char_ID)
    attributes = Attribute.objects.filter(char_ID=character)

    if attribute_type in Attribute.AttrTypes:
        attribute = attributes.get(_type=attribute_type)

        if is_training:
            raw_cost = attribute.training_cost

            if action_to_take >= 0:
                cost = action_to_take * raw_cost
                attribute.training_cost += 500
            else:
                cost = action_to_take * (raw_cost - 500)
                attribute.training_cost -= 500
            
            if cost > character.xp_current:
                return JsonResponse({'error': 'Not enough XP'}, status=500)
            
            attribute.training_level += action_to_take                
            attribute.save()
            character.xp_current -= cost
            character.save()
            return JsonResponse({'result': attribute.training_level, 'update_xp': character.xp_current})
        else:
            cost = action_to_take * attribute.attribute_point_cost
            if cost > character.xp_current:
                return JsonResponse({'error': 'Not enough XP'}, status=500)
            
            attribute.total_value += action_to_take
            attribute.save()
            character.xp_current -= cost
            character.save()
            return JsonResponse({'result': attribute.total_value, 'update_xp': character.xp_current})
    else:
        messages.error(request, 'Error')
        return redirect('evolve', char_ID=character.pk)

def upgrade_action(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    action_type = request.GET.get('action_type')
    action_to_take = int(request.GET.get('action_to_take'))
    dice = request.GET.get('dice')

    character = Character.objects.get(pk=char_ID)
    actions = Action.objects.filter(char_ID=character)

    if action_type in Action.ActionTypes:            
        action = actions.get(_type=action_type)
        cost = action_to_take * action.dice_cost[dice]
        if cost > character.xp_current:
            return JsonResponse({'error': 'Not enough XP'}, status=500)
        
        current = getattr(action, dice)
        setattr(action, dice, current + action_to_take)
        action.save()
        character.xp_current -= cost
        character.save()
        return JsonResponse({'result': getattr(action, dice), 'update_xp': character.xp_current})
    else:
        messages.error(request, 'Error')
        return redirect('evolve', char_ID=character.pk)

def upgrade_character_battle_actions(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    battle_action_type = request.GET.get('battle_action_type')
    action_to_take = int(request.GET.get('action_to_take'))

    character = Character.objects.get(pk=char_ID)

    if battle_action_type == 'movement' or battle_action_type == 'main':
        raw_cost = getattr(character, f'{battle_action_type}_action_cost')

        if action_to_take >= 0:
            cost = action_to_take * raw_cost
        else:
            cost = action_to_take * (raw_cost - (2000 if battle_action_type == 'movement' else 3000))

        if cost > character.xp_current:
            return JsonResponse({'error': 'Not enough XP'}, status=500)

        action_type = f'{battle_action_type}_actions'
        current = getattr(character, action_type)
        setattr(character, action_type, current + action_to_take)
        character.xp_current -= cost
        setattr(character, f'{battle_action_type}_action_cost', raw_cost + cost)
        character.save()
        
        json_data = {
            'result': getattr(character, action_type),
            'update_xp': character.xp_current,
            'new_cost': getattr(character, f'{battle_action_type}_action_cost')
        }
        return JsonResponse(json_data)
    else:
        messages.error(request, 'Error')
        return redirect('evolve', char_ID=character.pk)
    
# Views related to manipulating skills
@login_required
def skills(request, char_ID):
    character = Character.objects.get(id=char_ID)

    if AvailableSkill.objects.filter(char_ID=char_ID).exists():
        learned_skills = [
            skill.skill_ID for skill in AvailableSkill.objects.filter(char_ID=char_ID)
        ]
    else:
        learned_skills = []
    
    active_path = AvailablePath.objects.filter(char_ID=character).get(path_ID=character.active_path)
    active_path_skills = Skill.objects.filter(path=character.active_path).exclude(_category=Skill.Category.INTRINSIC)

    if request.method == 'POST':
        skill_ID = int(request.POST.get('skill_ID'))
        skill_to_learn = Skill.objects.get(id=skill_ID)

        # Deduct the skill cost from character's PP
        if active_path.current_pp >= skill_to_learn.cost:
            active_path.current_pp -= skill_to_learn.cost
            active_path.save()
        else:
            messages.error(request, 'PC insuficientes')
            return redirect('skills', char_ID=char_ID)

        # Add the skill to character's available skills
        skill_learned = AvailableSkill(char_ID=character, skill_ID=skill_to_learn)
        skill_learned.save()
        messages.success(request, f'{character.name} aprendeu a habilidade')

        return redirect('skills', char_ID=char_ID)

    skills_data = {
        'character': character,
        'learned_skills': learned_skills,
        'active_path': active_path,
        'active_path_skills': active_path_skills,
    }

    return render(request, 'sheet/learn.html', skills_data)

def equip_skill(request):
    if not is_ajax(request):
        return redirect('home')
    
    char_ID = int(request.GET.get('char_ID'))
    slot = request.GET.get('slot')
    skill_ID = int(request.GET.get('skill_ID'))
    
    character = Character.objects.get(pk=char_ID)
    equipped_skills = EquippedSkill.objects.get(char_ID=character)

    if skill_ID == 0:
        skill_to_equip = None
    else:
        skill_to_equip = Skill.objects.get(pk=skill_ID)

    setattr(equipped_skills, slot, skill_to_equip)

    equipped_skills.save()

    response = {'skill_description': skill_to_equip.description if skill_to_equip else ''}

    return JsonResponse(response)
        
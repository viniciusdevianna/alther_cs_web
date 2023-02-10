from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from sheet.models import *
from sheet.forms import CreateCharForm, AttributeForm

# Consts to take care of default values for character creation, have to incroporate them in the model lately
INITAL_CHAR_DATA = {
    'level': 1,
    'xp_total': 0.,
    'xp_current': 0,
    'hp_total': 10,
    'hp_current': 10,
    'hp_temp': 0,
    'unbalance': 0,
    'movement_actions': 1,
    'main_actions': 1,
    'inventory': '',
    'annotations': '',
    'coin': '0 valores'
}

INITIAL_PATH_DATA = {
    'current_pp': 0,
    'total_pp': 0,
    'level': 1,
    'is_master': False
}

INITIAL_ACTION_DATA = {
    'nd4': 0,
    'nd6': 0,
    'nd8': 1,
    'nd10': 0,
    'nd12': 0,
    'nd20': 0,
    'flat_bonus': 0,
    'flat_penalty': 0
}

def main(request, char_ID=None):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

    if request.method == 'POST':
        char_ID = request.POST.get('character')
    
    if char_ID is None:
        return redirect('pick_character')

    character = Character.objects.get(id=char_ID)
    actions = Action.objects.filter(char_ID=char_ID)
    attributes = Attribute.objects.filter(char_ID=char_ID)
    available_paths = AvailablePath.objects.filter(char_ID=char_ID)
    active_path = available_paths.get(path_ID=character.active_path)
    available_skills = AvailableSkill.objects.filter(char_ID=char_ID)
    equipped_skills = EquippedSkill.objects.get(char_ID=char_ID)
    equipped_skills_dict = {}
    
    for field in EquippedSkill._meta.get_fields()[2:]:
        equipped_skills_dict[field.name] = getattr(equipped_skills, field.name)

    char_data = {
        'character': character,
        'attributes': attributes,
        'available_paths': available_paths,
        'active_path': active_path,
        'available_skills': available_skills,
        'equipped_skills': equipped_skills,
        'equipped_skills_dict': equipped_skills_dict,
        'actions': actions,
    }

    return render(request, 'sheet/main.html', char_data)
    
# Views that manipulate data in the main sheet view
def roll_action(request):
    if request.accepts('application/json') and request.method == 'GET':
        action_ID = int(request.GET.get('action_ID'))
        action_to_roll = Action.objects.get(pk=action_ID)
        roll = action_to_roll.roll_dice()

        return JsonResponse({"roll": roll})
        
    return redirect('home')


def level_up(request):
    if request.accepts('application/json') and request.method == 'GET':
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

        return JsonResponse({'level': character.level, 'xp_current': character.xp_current, 'xp_total': character.xp_total})
    
    return redirect('home')


def update_basic(request):
    if request.accepts("application/json") and request.method == 'GET':
        char_ID = int(request.GET.get('char_ID'))
        info_to_update = request.GET.get('info_to_update')
        new_value = request.GET.get('new_value')

        character = Character.objects.get(pk=char_ID)
        old_value = getattr(character, info_to_update)

        if type(new_value) != type(old_value):
            new_value = type(old_value)(new_value)

        setattr(character, info_to_update, new_value)
        character.save()

        return JsonResponse({info_to_update: new_value})
    
    return redirect('home')


def manipulate_attribute(request):
    if request.accepts("application/json") and request.method == 'GET':
        attr_ID = int(request.GET.get('attr_ID'))
        operation = int(request.GET.get('operation'))

        attribute = Attribute.objects.get(pk=attr_ID)

        attribute.current_value += operation
        attribute.save()

        return JsonResponse({'new_value': attribute.current_value})

    return redirect('home')

def change_active_path(request):
    if request.accepts("application/json") and request.method == 'GET':
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
    
    return redirect('home')

def update_text(request):
    if request.accepts("application/json") and request.method == 'GET':
        char_ID = int(request.GET.get('char_ID'))
        info_to_update = request.GET.get('info_to_update')
        new_text = request.GET.get('new_text')

        character = Character.objects.get(pk=char_ID)
        setattr(character, info_to_update, new_text)
        character.save()

        return JsonResponse({'response': 'success'})
    
    return redirect('home')

def manipulate_pathpoints(request):
    if request.accepts("application/json") and request.method == 'GET':
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
    
    return redirect('home')

# Views for new sheet creation and editing char information outside of main sheet page
def create_character(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

    form = CreateCharForm()

    if request.method == 'POST':
        form = CreateCharForm(request.POST)

        if form.is_valid():
            player = request.user
            new_char = Character(player_ID=player, **INITAL_CHAR_DATA)
            new_char.active_path = Path.objects.get(pk='NOV')
            form = CreateCharForm(request.POST, instance=new_char)

            new_char = form.save()

            paths = Path.objects.filter(aspiration=new_char.aspiration, tier=Path.Tier.BASIC)
            for path in paths:
                available_path = AvailablePath(char_ID=new_char, path_ID=path, **INITIAL_PATH_DATA)
                available_path.save()
                
            active_initial_path = AvailablePath.objects.filter(char_ID=new_char).first()
            if active_initial_path is not None:
                new_char.active_path = active_initial_path.path_ID
                new_char.save()        

            intrinsic_skill = Skill.objects.filter(_category=Skill.Category.INTRINSIC).get(path=new_char.active_path)
            equipped_skill = EquippedSkill(char_ID=new_char, intrinsic=intrinsic_skill)
            equipped_skill.save()
            
            for action_type in Action.ActionTypes:
                new_action = Action(type=action_type, char_ID=new_char, **INITIAL_ACTION_DATA)
                new_action.save()
            
            return redirect('new_path', char_ID=new_char.pk)

    return render(request, 'sheet/create.html', {'form': form})

def update_attributes(request, char_ID):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

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
        'character': char_ID,
        'available_paths': available_paths,
        'aspiration_paths': aspiration_paths
    }

    return render(request, 'sheet/newpath.html', paths_data)

# Views related to manipulating skills
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
    if request.accepts('application/json') and request.method == 'GET':
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

        return JsonResponse({'skill_description': skill_to_equip.description if skill_to_equip else ''})

    return redirect('home')
        
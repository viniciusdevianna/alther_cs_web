from django.shortcuts import render, redirect
from django.contrib import messages
from sheet.models import *
from sheet.forms import CreateCharForm, AttributeForm

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

def main(request, char_ID):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

    character = Character.objects.get(id=char_ID)
    actions = Action.objects.filter(char_ID=char_ID)
    attributes = Attribute.objects.filter(char_ID=char_ID)
    active_path = AvailablePath.objects.filter(char_ID=char_ID).get(path_ID=character.active_path)
    equipped_skills = EquippedSkill.objects.get(char_ID=char_ID)

    char_data = {
        'character': character,
        'actions': actions,
        'attributes': attributes,
        'active_path': active_path,
        'equipped_skills': equipped_skills,
    }
    return render(request, 'sheet/main.html', char_data)

def roll_action(request, action_ID):
    action = Action.objects.get(id=action_ID)
    char_ID = action.char_ID.pk
    print(action.roll_dice()['result'])
    return redirect('main', char_ID=char_ID)

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
            form = CreateCharForm(request.POST, instance=new_char)

            new_char = form.save()

            paths = Path.objects.filter(aspiration=new_char.aspiration, tier=Path.Tier.BASIC)
            for path in paths:
                available_path = AvailablePath(char_ID=new_char, path_ID=path, **INITIAL_PATH_DATA)                
                skill_to_learn = Skill.objects.filter(_category=Skill.Category.INTRINSIC).get(path=path)
                available_skill = AvailableSkill(char_ID=new_char, skill_ID=skill_to_learn)
                available_path.save()
                available_skill.save()

            active_initial_path = AvailablePath.objects.filter(char_ID=new_char).get(path_ID=new_char.active_path)
            active_initial_path.total_pp = 100
            active_initial_path.current_pp = active_initial_path.total_pp
            active_initial_path.save()

            intrinsic_skill = Skill.objects.filter(_category=Skill.Category.INTRINSIC).get(path=new_char.active_path)
            equipped_skill = EquippedSkill(char_ID=new_char, intrinsic=intrinsic_skill)
            equipped_skill.save()
            
            for action_type in Action.ActionTypes:
                new_action = Action(type=action_type, char_ID=new_char, **INITIAL_ACTION_DATA)
                new_action.save()
            
            return redirect('update_attributes', char_ID=new_char.id)

    return render(request, 'sheet/create.html', {'form': form})

def update_attributes(request, char_ID):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

    character = Character.objects.get(id=char_ID)
    if Attribute.objects.filter(char_ID=char_ID).exists():
        attributes = Attribute.objects.filter(char_ID=char_ID)
    else:
        attributes = (
            Attribute(char_ID=character, type=this_type) for this_type in Attribute.AttrTypes
        )

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
            return redirect('skills', char_ID=char_ID)
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

def skills(request, char_ID):
    character = Character.objects.get(id=char_ID)

    if AvailableSkill.objects.filter(char_ID=char_ID).exists():
        learned_skills = [
            skill.skill_ID for skill in AvailableSkill.objects.filter(char_ID=char_ID)
        ]
    else:
        learned_skills = []
    
    active_path = AvailablePath.objects.filter(char_ID=char_ID).get(path_ID=character.active_path)
    active_path_skills = Skill.objects.filter(path=character.active_path)

    if request.method == 'POST':
        print(request.POST)
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
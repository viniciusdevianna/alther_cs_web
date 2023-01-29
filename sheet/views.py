from django.shortcuts import render, redirect
from django.contrib import messages
from sheet.models import Action, Character, Attribute, AvailablePath, EquippedSkill

def main(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não reconhecido')
        return redirect('login')

    char_ID = 2
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
    print(action.roll_dice()['result'])
    return redirect('main')

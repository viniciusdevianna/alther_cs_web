from django.shortcuts import render, redirect
from sheet.models import Action, Character, Attribute

def index(request):
    char_ID = 2
    character = Character.objects.get(id=char_ID)
    actions = Action.objects.filter(char_ID=char_ID)
    attributes = Attribute.objects.filter(char_ID=char_ID)

    char_data = {
        'character': character,
        'actions': actions,
        'attributes': attributes,
    }
    return render(request, 'sheet/index.html', char_data)

def roll_action(request, action_ID):
    action = Action.objects.get(id=action_ID)
    print(action.roll_dice()['result'])
    return redirect('index')

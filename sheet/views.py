from django.shortcuts import render, redirect
from sheet.models import Action

def index(request):
    action = Action.objects.get(id=1)
    result = action.roll_dice()['result']
    return render(request, 'sheet/index.html', {'action': action, 'result': result})


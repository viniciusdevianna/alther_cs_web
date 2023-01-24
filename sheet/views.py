from django.shortcuts import render
from sheet.models import School

def index(request):
    schools = School.objects.all()
    return render(request, 'sheet/index.html', {'schools': schools})

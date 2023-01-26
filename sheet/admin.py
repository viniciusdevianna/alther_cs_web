from django.contrib import admin
from django.apps import apps
from sheet.models import *

admin.site.register(apps.all_models['sheet'].values())

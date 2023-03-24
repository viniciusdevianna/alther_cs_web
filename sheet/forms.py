from django import forms
from sheet.models import Character, Attribute, Aspiration, Action

class CreateCharForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateCharForm, self).__init__(*args, **kwargs)
        self.fields['aspiration'].queryset = Aspiration.objects.exclude(
            pk='PRO'
        )
        
    class Meta:
        model = Character
        fields = [
            'name',
            'origin',
            'race',
            'weight',
            'height',
            'age',
            'school',
            'aspiration',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'origin': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'race': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'weight': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'height': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'school': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'aspiration': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = [
            'current_value',
            'total_value',
            'temp_value',
            'training_level',
        ]
        widgets = {
            'current_value': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'total_value': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'temp_value': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'training_level': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
        }

class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = [
            'nd4',
            'nd6',
            'nd8',
            'nd10',
            'nd12',
            'nd20',
            'flat_bonus',
            'flat_penalty',
        ]
        widgets = {
            'nd4': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end',
                }
            ),
            'nd6': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'nd8': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'nd10': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'nd12': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'nd20': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'flat_bonus': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
            'flat_penalty': forms.NumberInput(
                attrs={
                    'class': 'form-control text-end'
                }
            ),
        }
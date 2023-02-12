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

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = [
            'current_value',
            'total_value',
            'temp_value',
            'training_level',
        ]

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
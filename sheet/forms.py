from django import forms
from sheet.models import Character, Path, Attribute

class CreateCharForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateCharForm, self).__init__(*args, **kwargs)
        self.fields['active_path'].queryset = Path.objects.filter(
            tier=1
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
            'active_path',
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

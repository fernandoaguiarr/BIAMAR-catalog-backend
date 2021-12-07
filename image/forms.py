from django import forms

from utils.models import ExportFor


class PhotoForm(forms.ModelForm):
    export_to = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=ExportFor.objects.filter(category=1),
    )

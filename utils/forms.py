from django import forms

from utils.models import ExportForTypes


class ExportForForm(forms.ModelForm):
    category = forms.IntegerField(widget=forms.RadioSelect(choices=ExportForTypes.choices))

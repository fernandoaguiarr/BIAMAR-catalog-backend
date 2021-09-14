from django import forms

from utils.models import ExportFor


class PhotoForm(forms.ModelForm):
    export_to = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=ExportFor.objects.filter(category=1).values_list('id', 'name'),
        show_hidden_initial=True,
    )

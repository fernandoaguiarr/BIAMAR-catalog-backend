from django import forms

from image.models import Photo
from utils.models import ExportFor


class PhotoForm(forms.ModelForm):
    export_to = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=ExportFor.objects.filter(category=1),
    )

    class Meta:
        model = Photo
        fields = '__all__'

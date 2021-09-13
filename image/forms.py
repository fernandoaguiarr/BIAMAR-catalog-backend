from django import forms

from image.models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['category', 'color', 'file', 'export_for']
        widgets = {'export_for': forms.CheckboxSelectMultiple}

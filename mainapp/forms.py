from django import forms
from .models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image-upload'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

        
from django import forms
from django.db.models import fields
from .models import *

class PhotoUploadForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['user', 'image', 'caption']
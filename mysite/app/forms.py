from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
from django import forms

class DirectoryForm(forms.ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'description', 'parentDirectory', 'owner']

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'description','fileField', 'directory', 'owner']

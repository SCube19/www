from django.forms import widgets
from .models import User, File, FileSection, Directory, SectionCategory, Status, StatusData
from django import forms

acceptedProvers = {'Default', 'alt-ergo', 'CVC4', 'z3'}
acceptedFlags = {'@lemma', '@requires', '@assigns', '@ensures', '@exits', '@assert',
'@check', '@invariant', '@variant', '@breaks', '@continues', '@returns',
'@complete_behaviors', '@disjoint_behaviors'}

class DirectoryForm(forms.ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'description', 'parentDirectory']

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'description','fileField', 'directory']

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    class Meta:
        model = User
        fields = ['login', 'password']
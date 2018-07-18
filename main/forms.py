from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Project
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import login


class ProjectCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if kwargs.has_key("request"):
            self.request = kwargs.pop("request")
        else:
            self.request = None
        super(ProjectCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['name', 'description', 'image', 'longitude', 'latitude', 'title', 'address']
        widgets = {
            'description': forms.Textarea(attrs={'minlength': '80', 'style': 'width: 100%'}),
            'longitude': forms.NumberInput(attrs={'id': 'longitude', 'style': 'display:none'}),
            'latitude': forms.NumberInput(attrs={'id': 'latitude', 'style': 'display:none'}),

        }

    def save(self, commit=True):

        if self.request is not None:
            project = Project()
            project.user = self.request.user
        else:
            project = self.project

        project.name = self.cleaned_data['name']

        project.description = self.cleaned_data['description']
        project.image = self.cleaned_data['image']
        project.title = self.cleaned_data['title']

        project.address = self.cleaned_data['address']
        project.longitude = float(self.cleaned_data['longitude'])
        project.latitude = float(self.cleaned_data['latitude'])

        if commit:
            project.save()
        return project


class UserProfileForm(forms.ModelForm):
    image = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def has_no_value(self, field):
        if len(self.cleaned_data[field]) == 0:
            raise ValidationError("this field cannot be empty")
        return self.cleaned_data[field]

    def clean_email(self):
        return self.has_no_value('email')

    def clean_first_name(self):
        return self.has_no_value('first_name')

    def clean_last_name(self):
        return self.has_no_value('last_name')

    def save(self, commit=True):
        user = self.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data['image']:
            user.profile.image = self.cleaned_data['image']

        if commit:
            user.profile.save()
            user.save()

        return user


class PasswordChangeForm(UserCreationForm):


    class Meta:
        model = User

        fields = ['password1', 'password2']
        exclude = ('username', 'email', 'password', 'first_name', 'last_name')

    def save(self, commit=True):
        user = self.request.user
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            login(self.request, user)
        return user

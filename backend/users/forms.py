from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


def _bootstrap_fields(form):
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)

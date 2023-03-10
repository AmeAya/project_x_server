from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUserModel
from django import forms
from django.contrib.auth import authenticate, get_user_model


class CustomUserCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    class Meta:
        model = CustomUserModel
        fields = (
            'phone',
            'first_name',
            'last_name',
            'iin',
            'position'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUserModel
        fields = (
            'phone',
            'first_name',
            'last_name',
            'iin',
            'position'
        )

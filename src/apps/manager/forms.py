from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from src.apps.manager.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    """Form for changing users."""

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

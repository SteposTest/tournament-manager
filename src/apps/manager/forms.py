from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from src.apps.manager.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'nickname',
            'telegram_username',
            'is_admin',
            'timezone',
            'fifa_versions',
        )


class CustomUserChangeForm(UserChangeForm):
    """Form for changing users."""

    class Meta:
        model = CustomUser
        fields = ('username', 'nickname', 'telegram_username', 'is_admin', 'fifa_versions', 'timezone')

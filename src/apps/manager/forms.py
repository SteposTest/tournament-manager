from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from src.apps.manager.models import CustomUser, Team
from src.utils.enums import FIFAVersion, Country


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


class TeamForm(forms.ModelForm):
    """Form for creating a new Team."""

    fifa_version = forms.ChoiceField(choices=FIFAVersion.choices(), label='FIFA Version')
    country = forms.ChoiceField(choices=Country.choices(), label='Country')

    class Meta:
        model = Team
        fields = (
            'name',
            'league',
            'country',
            'img_url',
            'rating',
            'attack',
            'midfield',
            'defense',
            'general',
            'fifa_version',
        )

    def save(self, commit=True):
        """Save the provided team instance."""
        team = super().save(commit=False)
        if commit:
            team.save()
        return team

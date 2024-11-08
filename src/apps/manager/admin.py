from django.contrib import admin

from src.apps.manager.forms import CustomUserChangeForm, CustomUserCreationForm
from src.apps.manager.models import CustomUser, Team, Tournament, Game


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin model for CustomUser."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'telegram_username']
    search_fields = ['username', 'telegram_username']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin model for Team."""

    list_display = ('name', 'rating', 'attack', 'midfield', 'defense')
    list_filter = ('country', 'fifa_version')
    search_fields = ('name', 'country', 'fifa_version')


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """Admin model for Tournament."""

    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'fifa_version')
    search_fields = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin model for Game."""

    list_display = (
        'date',
        'is_completed',
        'first_player',
        'second_player',
    )
    list_filter = ('is_completed', 'date')
    search_fields = ('first_player__name', 'second_player__name')
    autocomplete_fields = ('first_player', 'second_player', 'first_player_team', 'second_player_team')

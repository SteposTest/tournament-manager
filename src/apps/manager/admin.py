from django.contrib import admin

from src.apps.manager.forms import CustomUserChangeForm, CustomUserCreationForm, TeamForm
from src.apps.manager.models import CustomUser, Team, Tournament, Game, League


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin model for CustomUser."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'username',
        'nickname',
        'telegram_username',
        'is_admin',
        'timezone',
        'victories',
        'losses',
        'draws',
        'fifa_versions',
    ]
    search_fields = ['username', 'nickname', 'telegram_username', 'is_admin', 'telegram_user_id', 'telegram_chat_id']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin model for Team."""

    form = TeamForm

    list_display = ('name', 'general', 'rating', 'attack', 'midfield', 'defense', 'fifa_version')
    list_filter = ('fifa_version', 'league')
    search_fields = ('name', 'fifa_version', 'rating')


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin model for League."""

    list_display = ('name', 'country')
    search_fields = ('country',)


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
    autocomplete_fields = (
        'first_player',
        'second_player',
        'first_player_team',
        'second_player_team',
    )

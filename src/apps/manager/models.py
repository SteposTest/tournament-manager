import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from src.utils.enums import Country, FIFAVersion


class CustomUser(AbstractUser):
    """CustomUser model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    timezone = models.CharField(max_length=32, default='UTC')

    telegram_user_id = models.IntegerField(blank=True, null=True)
    telegram_chat_id = models.IntegerField(blank=True, null=True)
    telegram_username = models.CharField(max_length=64, unique=True)

    victories = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    fifa_versions = models.JSONField(default=list)

    def __str__(self):
        return self.username

    def get_future_games(self) -> list['Game']:
        """Return scheduled games."""
        result = [self.games_as_first.filter(is_completed=False)]
        result.extend(self.games_as_second.filter(is_completed=False))
        return result

    def get_completed_games(self) -> list['Game']:
        """Return completed games."""
        result = [self.games_as_first.filter(is_completed=True)]
        result.extend(self.games_as_second.filter(is_completed=True))
        return result


class Tournament(models.Model):
    """Tournament model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=128)
    rules_url = models.URLField()
    start_date = models.DateField()
    circles_number = models.PositiveIntegerField()
    fifa_version = models.IntegerField(choices=FIFAVersion.choices)
    end_date = models.DateField(blank=True, null=True)

    participants = models.ManyToManyField(to='CustomUser', related_name='tournaments')
    available_teams = models.ManyToManyField('Team', related_name='tournaments')

    def __str__(self):
        return self.name

    def get_future_games(self) -> list['Game']:
        """Return scheduled games."""
        return self.games.filter(is_completed=False)

    def get_completed_games(self) -> list['Game']:
        """Return completed games."""
        return self.games.filter(is_completed=True)


class Game(models.Model):
    """Game model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    tournament = models.ForeignKey(to='Tournament', related_name='games', on_delete=models.CASCADE)

    first_player_score = models.PositiveIntegerField(blank=True, null=True)
    second_player_score = models.PositiveIntegerField(blank=True, null=True)

    first_player = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, related_name='games_as_first')
    second_player = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, related_name='games_as_second')

    first_player_team = models.ForeignKey(to='Team', on_delete=models.CASCADE, related_name='games_as_first_team')
    second_player_team = models.ForeignKey(to='Team', on_delete=models.CASCADE, related_name='games_as_second_team')

    def __str__(self):
        return f'{self.first_player} vs {self.second_player} on {self.date}'

    def get_participants(self) -> list[CustomUser]:
        """Return participants."""
        return [self.first_player, self.second_player]

    def get_player_team_and_score(self, player: 'CustomUser') -> 'Team':
        """Return player team."""
        return self.first_player_team if self._is_first_player(player) else self.second_player_team

    def get_player_score(self, player: 'CustomUser') -> int:
        """Return player score."""
        return self.first_player_score if self._is_first_player(player) else self.second_player_score

    def _is_first_player(self, player: 'CustomUser') -> bool:
        return player == self.first_player


class Team(models.Model):
    """Team model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    league = models.ForeignKey(to='League', on_delete=models.CASCADE, related_name='teams')
    img_url = models.URLField(blank=True, null=True)
    fifa_version = models.IntegerField(choices=FIFAVersion.choices)
    rating = models.FloatField()
    attack = models.PositiveIntegerField()
    midfield = models.PositiveIntegerField()
    defense = models.PositiveIntegerField()
    general = models.PositiveIntegerField()

    @property
    def country(self) -> Country | None:
        """Take the country from the team league and return."""
        country = self.league.country
        if country is not None:
            return Country(country)

    def __str__(self):
        return f'{self.name} - {self.country if self.country is not None else "Unknown country"}'


class League(models.Model):
    """League model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    country = models.IntegerField(choices=Country.choices, blank=True, null=True)

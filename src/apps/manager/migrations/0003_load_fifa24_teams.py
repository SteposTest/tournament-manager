import json
import pathlib

from django.db import migrations

from src.utils.enums import FIFAVersion

ADDITIONAL_FILES_PATH = pathlib.Path(__file__).parent.resolve().joinpath('additional_files')


def load_data(apps, _):
    League = apps.get_model('manager', 'League')
    Team = apps.get_model('manager', 'Team')

    teams_file = ADDITIONAL_FILES_PATH.joinpath('fifa24_teams.json')

    with open(teams_file, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)

    for team in teams_data:
        league = League.objects.get(name=team['league'])

        Team.objects.create(
            name=team['name'],
            country=league.country,
            league=league,
            img_url=team.get('img_url'),
            attack=team['attack'],
            midfield=team['midfield'],
            defense=team['defense'],
            general=team['general'],
            rating=team['rating'],
            fifa_version=FIFAVersion.FIFA24,
        )


def unload_data(apps, _):
    Team = apps.get_model('manager', 'Team')
    Team.objects.filter(fifa_version=FIFAVersion.FIFA24).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0002_load_leagues'),
    ]

    operations = [
        migrations.RunPython(load_data, reverse_code=unload_data),
    ]

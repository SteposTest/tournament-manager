import json
import pathlib

from django.db import migrations

from src.utils.enums import Country

ADDITIONAL_FILES_PATH = pathlib.Path(__file__).parent.resolve().joinpath('additional_files')


def load_data(apps, _):
    League = apps.get_model('manager', 'League')

    leagues_file = ADDITIONAL_FILES_PATH.joinpath('fifa24_leagues.json')

    with open(leagues_file, 'r', encoding='utf-8') as f:
        leagues_data = json.load(f)

    league_mapping = {}
    for league in leagues_data:
        country = league['country']
        league_obj, created = League.objects.get_or_create(
            name=league['name'],
            country=Country.from_string(country) if country else None,
        )
        league_mapping[league['name']] = league_obj


def unload_data(apps, _):
    League = apps.get_model('manager', 'League')
    League.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data, reverse_code=unload_data),
    ]

import os
from functools import lru_cache
from typing import List

import yaml
from django.conf import settings

from src.config.settings import LANGUAGE_PACKAGES_PATH
from src.language.models import BotPhrases, BotRepresentation


def get_available_languages_codes() -> List[str]:
    """Return a list of available language codes."""
    return os.listdir(LANGUAGE_PACKAGES_PATH)


@lru_cache()
def get_bot_phrases(language_code: str | None) -> BotPhrases:
    """
    Builds and returns an BotPhrases object with bot phrases in the specified language, if any.

    By default, the language is Russian.
    """
    _language_code = _get_language_code(language_code)
    package_yaml = _get_language_pack(
        language_code=_language_code,
        package_name='bot_phrases',
    )

    return BotPhrases(language_code=_language_code, **package_yaml)


@lru_cache()
def get_bot_representation_pack(language_code: str | None) -> BotRepresentation:
    """
    Builds and returns an BotCommandsRepresentation object with bot phrases in the specified language, if any.

    By default, the language is Russian.
    """
    _language_code = _get_language_code(language_code)
    package_yaml = _get_language_pack(
        language_code=_language_code,
        package_name='bot_representation',
    )
    return BotRepresentation(
        language_code=_language_code,
        **package_yaml,
    )


def _get_language_pack(language_code: str, package_name: str) -> dict:
    with open(os.path.join(LANGUAGE_PACKAGES_PATH, f'{language_code}/{package_name}.yaml'), 'r') as package_obj:
        return yaml.safe_load(package_obj)


def _get_language_code(language_code: str | None = 'ru') -> str:
    available_codes = get_available_languages_codes()
    if language_code in available_codes:
        return language_code

    return settings.DEFAULT_LANGUAGE

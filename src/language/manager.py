import os
from functools import lru_cache
from typing import List

import yaml
from django.conf import settings

from src.config.settings import LANGUAGE_PACKAGES_PATH
from src.language.models import BotPhrases, BotCommandsDescription


def get_available_languages_codes() -> List[str]:
    """Return a list of available language codes."""
    return os.listdir(LANGUAGE_PACKAGES_PATH)


@lru_cache()
def get_bot_phrases(language_code: str | None) -> BotPhrases:
    """
    Builds and returns an BotPhrases object with bot phrases in the specified language, if any.

    By default, the language is Russian.
    """
    package_yaml = _get_language_pack(
        language_code=language_code,
        package_name='bot_phrases',
    )
    return BotPhrases(**package_yaml)


@lru_cache()
def get_bot_commands_description(language_code: str | None) -> BotCommandsDescription:
    """
    Builds and returns an BotCommandsDescription object with bot phrases in the specified language, if any.

    By default, the language is Russian.
    """
    package_yaml = _get_language_pack(
        language_code=language_code,
        package_name='bot_commands',
    )
    return BotCommandsDescription(**package_yaml)


def _get_language_pack(language_code: str | None, package_name: str) -> dict:
    lang_code = _get_language_code(language_code)
    with open(os.path.join(LANGUAGE_PACKAGES_PATH, f'{lang_code}/{package_name}.yaml'), 'r') as package_obj:
        return yaml.safe_load(package_obj)


def _get_language_code(language_code: str | None = 'ru') -> str:
    available_codes = get_available_languages_codes()
    if language_code in available_codes:
        return language_code

    return settings.DEFAULT_LANGUAGE_CODE

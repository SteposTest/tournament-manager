from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.bot_command import BotCommand

from src.language.manager import (
    get_bot_representation_pack,
    get_available_languages_codes,
)
from src.language.models import BotRepresentation
from src.utils.log import async_log, LOWEST_LOG_LVL, get_logger


async def set_bot_representation(bot: Bot):
    """Set bot command, description etc."""
    languages_codes = get_available_languages_codes()

    for code in languages_codes:
        commands_pack = get_bot_representation_pack(code)

        try:  # noqa: WPS229
            await _set_bot_commands(bot=bot, commands_pack=commands_pack, language_code=code)
            await _set_bot_description(bot=bot, commands_pack=commands_pack, language_code=code)
        except TelegramBadRequest:
            get_logger().warning('The descriptions of the bot were not provided.')


@async_log(lvl=LOWEST_LOG_LVL)
async def _set_bot_commands(bot: Bot, commands_pack: BotRepresentation, language_code: str):
    commands = []
    for command in commands_pack.model_fields:
        commands.append(
            BotCommand(
                command=f'/{command}',
                description=getattr(commands_pack, command),
            ),
        )

    await bot.set_my_commands(commands=commands, language_code=language_code)


@async_log(lvl=LOWEST_LOG_LVL)
async def _set_bot_description(bot: Bot, commands_pack: BotRepresentation, language_code: str):
    await bot.set_my_description(description=commands_pack.description, language_code=language_code)
    await bot.set_my_short_description(short_description=commands_pack.short_description, language_code=language_code)

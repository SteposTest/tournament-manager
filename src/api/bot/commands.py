from aiogram import Bot
from aiogram.types.bot_command import BotCommand

from src.language.manager import (
    get_bot_commands_description,
    get_available_languages_codes,
)


async def set_bot_commands(bot: Bot):
    """Set bot commands."""
    languages_codes = get_available_languages_codes()

    for code in languages_codes:
        commands_pack = get_bot_commands_description(code)

        commands = []
        for command in commands_pack.model_fields:
            commands.append(
                BotCommand(
                    command=f'/{command}',
                    description=getattr(commands_pack, command),
                ),
            )

        await bot.set_my_commands(commands=commands, language_code=code)

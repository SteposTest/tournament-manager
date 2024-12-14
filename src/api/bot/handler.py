import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.apps.manager.models import CustomUser as InternalUser
from src.config import settings
from src.language.manager import get_bot_phrases
from src.utils.log import async_log

router = Router()
logger = logging.getLogger(settings.LOGGER_NAME)


@async_log(lvl=logging.INFO)
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    telegram_user = message.from_user
    language_pack = get_bot_phrases(telegram_user.language_code)
    internal_user = await InternalUser.objects.filter(telegram_username=telegram_user.username).afirst()
    if internal_user is None:
        await message.answer(text=language_pack.user_not_found.format(message.from_user.full_name))

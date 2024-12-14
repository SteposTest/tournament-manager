import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, User
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config import settings
from src.language.manager import get_bot_phrases
from src.utils.log import async_log

router = Router()
logger = logging.getLogger(settings.LOGGER_NAME)


class StartCallback(CallbackData, prefix='start'):
    """Callback for the start command."""

    answer: bool


async def registrate_user(telegram_user: User):
    """Test user registration."""
    logger.info(f'User {telegram_user.username} (id: {telegram_user.id}) registered')


@async_log(lvl=logging.INFO)
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    language_pack = get_bot_phrases(message.from_user.language_code)
    builder = InlineKeyboardBuilder()

    builder.button(
        text=language_pack.reg_msg_answer_yes,
        callback_data=StartCallback(answer=True).pack(),
    )
    builder.button(
        text=language_pack.reg_msg_answer_no,
        callback_data=StartCallback(answer=False).pack(),
    )
    builder.adjust(2, 2)

    await message.answer(
        text=language_pack.reg_msg.format(message.from_user.full_name),
        reply_markup=builder.as_markup(),
    )


@async_log(lvl=logging.INFO)
@router.callback_query(StartCallback.filter)
async def process_registration_choice(call: CallbackQuery):
    """Process registration choice."""
    language_pack = get_bot_phrases(call.from_user.language_code)
    choice = bool(int(call.data.split(':')[1]))

    if choice:
        await registrate_user(call.from_user)
        response_text = language_pack.reg_done
        await call.message.answer(response_text)
    else:
        await call.message.answer(language_pack.reg_reject)

    await call.answer()

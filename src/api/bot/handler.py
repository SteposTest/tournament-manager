import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from src.bot.callbacks import QuestionCallback, NumericCallback
from src.bot.utils import build_main_reply_keyboard, get_internal_user_with_language_pack
from src.config import settings
from src.utils.log import async_log
from src.bot.bot_controller import get_bot_controller

router = Router()
logger = logging.getLogger(settings.LOGGER_NAME)

bot_controller = get_bot_controller()


@router.message(CommandStart())
@async_log(lvl=logging.INFO)
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    internal_user, bot_phrases = await get_internal_user_with_language_pack(message.from_user)
    if internal_user is not None:
        answer_text = bot_phrases.welcome_msg.format(internal_user.nickname)
    else:
        answer_text = bot_phrases.user_not_found.format(message.from_user.full_name)

    await message.answer(
        text=answer_text,
        reply_markup=await build_main_reply_keyboard(internal_user, bot_phrases),
    )


@router.message()
async def base_handler(message: Message) -> None:
    """This handler receives all messages."""
    await bot_controller.pass_message_to_processor(message)


@router.callback_query(QuestionCallback.filter)
async def handle_question_callback(query: CallbackQuery):
    """Process registration choice."""
    await bot_controller.pass_query_to_processor(query)


@router.callback_query(NumericCallback.filter)
async def handle_numeric_callback(query: CallbackQuery):
    """Process registration choice."""
    await bot_controller.pass_query_to_processor(query)

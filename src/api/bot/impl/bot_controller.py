from typing import Callable

from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.api.bot.impl import exceptions
from src.api.bot.impl.callbacks import QuestionCallback
from src.api.bot.impl.models import StateName, StateModel, Process
from src.api.bot.impl.utils import get_internal_user_with_language_pack
from src.apps.manager.models import CustomUser as InternalUser
from src.language.models import BotPhrases
from src.utils.log import get_logger

logger = get_logger(__name__)

STATE = dict()  # noqa C408


async def pass_message_to_handler(message: Message) -> None:
    """Find a handler and send a message to it."""
    internal_user, bot_phrases = await get_internal_user_with_language_pack(message.from_user)
    state: StateModel | None = STATE.get(message.chat.id)

    process = state.process if state else None
    try:
        message_handler = await _get_handler_by_process_or_message(
            bot_phrases=bot_phrases,
            process=process,
            message=message.text,
        )
    except exceptions.ProcessHandlerNotFound:
        raise exceptions.MessageHandlerNotFound(
            f'Handler for message "{message.text}" not found. '
            + f'Chat id {message.chat.id}. User {message.from_user.full_name}',
        )

    await message_handler(
        message=message,
        query=None,
        bot_phrases=bot_phrases,
        state=state,
        internal_user=internal_user,
    )


async def pass_query_to_handler(query: CallbackQuery) -> None:
    """Find a handler and send a query to it."""
    internal_user, bot_phrases = await get_internal_user_with_language_pack(query.from_user)
    state: StateModel | None = STATE.get(query.message.chat.id)

    if state is None or not state.is_query:
        logger.warning(
            f'State for query "{query.id}" not found. '
            + f'Chat id {query.message.chat.id}. User {query.from_user.full_name}',
        )
        await query.message.answer(bot_phrases.wrong_btn_pressing)
        return

    try:
        message_handler = await _get_handler_by_process_or_message(
            bot_phrases=bot_phrases,
            process=state.process,
        )
    except exceptions.ProcessHandlerNotFound:
        raise exceptions.QueryHandlerNotFound(
            f'Handler for query "{query.id}" not found. '
            + f'Chat id {query.message.chat.id}. User {query.from_user.full_name}',
        )

    await message_handler(
        message=None,
        query=query,
        bot_phrases=bot_phrases,
        state=state,
        internal_user=internal_user,
    )


async def _get_handler_by_process_or_message(
    bot_phrases: BotPhrases,
    process: str | None,
    message: str | None = None,
) -> Callable:
    match process or message:
        case Process.REGISTRATION.value | bot_phrases.registrate_btn:
            return registration_process
        case _:
            raise exceptions.ProcessHandlerNotFound(f'Handler for process "{process}" not found.')


async def registration_process(
    message: Message | None,
    query: CallbackQuery | None,
    bot_phrases: BotPhrases,
    state: StateModel | None,
    internal_user: InternalUser | None,  # noqa
) -> None:
    """The user registration process."""
    chat_id = message.chat.id if message else query.message.chat.id
    if state is None:
        STATE[chat_id] = StateModel(process=Process.REGISTRATION, name=StateName.REG_EXPECT_NICKNAME)
        await message.answer(bot_phrases.reg_nickname_request)
        return

    match state.name:
        case StateName.REG_EXPECT_NICKNAME:
            potential_nickname = message.text
            is_nickname_in_use = await InternalUser.objects.filter(nickname=potential_nickname).aexists()
            if is_nickname_in_use:
                await message.answer(bot_phrases.reg_nickname_in_use)
                return

            builder = InlineKeyboardBuilder()

            builder.button(text=bot_phrases.yes_btn, callback_data=QuestionCallback(answer=bot_phrases.yes_btn).pack())
            builder.button(text=bot_phrases.no_btn, callback_data=QuestionCallback(answer=bot_phrases.no_btn).pack())
            builder.adjust(2)

            await message.answer(
                text=bot_phrases.reg_confirm.format(potential_nickname),
                reply_markup=builder.as_markup(),
            )
            STATE[chat_id] = StateModel(
                process=Process.REGISTRATION,
                name=StateName.REG_EXPECT_CONFIRM,
                is_query=True,
                payload=potential_nickname,
            )
        case StateName.REG_EXPECT_CONFIRM:
            potential_nickname = state.payload
            answer = query.data.split(':')[1]
            if answer == bot_phrases.yes_btn:
                telegram_user = query.from_user
                new_internal_user = InternalUser(
                    nickname=potential_nickname,
                    telegram_user_id=telegram_user.id,
                    telegram_username=telegram_user.username,
                    telegram_chat_id=query.message.chat.id,
                )
                await new_internal_user.asave()

                STATE.pop(chat_id)
                await query.answer(bot_phrases.reg_done)
            elif answer == bot_phrases.no_btn:
                STATE[chat_id] = StateModel(
                    process=Process.REGISTRATION,
                    name=StateName.REG_EXPECT_NICKNAME,
                )
                await query.message.answer(bot_phrases.reg_nickname_request_again)
                return

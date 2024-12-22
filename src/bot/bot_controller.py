import random
from functools import lru_cache

from aiogram.client.bot import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from src.bot import exceptions, processors
from src.bot.models import ProcessName, StateModel, MessageNewData
from src.bot.state_controller import StateController
from src.bot.utils import get_internal_user_with_language_pack
from src.language.models import BotPhrases
from src.runner import telegram_bot
from src.utils.log import get_logger, async_log, LOWEST_LOG_LVL

logger = get_logger(__name__)


class BotController:
    """Processing of all bot operations."""

    def __init__(self, bot: Bot):
        self.bot = bot

        self.state_controller = StateController()

        self.registration_processor = processors.RegistrationProcessor(self.state_controller)
        self.team_choosing_process = processors.TeamChoosingProcessor(self.state_controller)

    async def pass_message_to_processor(self, message: Message) -> None:
        """Find a processor and send a message to it."""
        internal_user, bot_phrases = await get_internal_user_with_language_pack(message.from_user)
        state = self.state_controller.get_state(message.chat.id)
        if state is not None and state.is_query:
            await message.answer(random.choice(bot_phrases.wrong_msg))
            return

        await self._update_messages(message.chat.id, self.bot)

        process = state.process_name if state else None
        try:
            processor = await self._get_processor(bot_phrases=bot_phrases, process=process, message=message.text)
        except exceptions.ProcessHandlerNotFound:
            logger.warning(
                f'Handler for message "{message.text}" not found. '
                + f'Chat id {message.chat.id}. User {message.from_user.full_name}',
            )
            await message.answer(random.choice(bot_phrases.wrong_msg))
            return

        await processor.process(
            message=message,
            query=None,
            bot_phrases=bot_phrases,
            internal_user=internal_user,
        )

        new_state = self.state_controller.get_state(message.chat.id)
        if new_state and new_state.is_complete:
            await self._update_messages(message.chat.id, message.bot)
            self.state_controller.delete_state(state.chat_id)

    async def pass_query_to_processor(self, query: CallbackQuery) -> None:
        """Find a handler and send a query to it."""
        internal_user, bot_phrases = await get_internal_user_with_language_pack(query.from_user)
        state = self.state_controller.get_state(query.message.chat.id)
        await self._update_messages(query.message.chat.id, query.bot)

        if state is None or not state.is_query:
            logger.warning(
                f'State for query "{query.id}" not found. '
                + f'Chat id {query.message.chat.id}. User {query.from_user.full_name}',
            )
            await query.message.answer(bot_phrases.wrong_btn_pressing)
            return

        try:
            processor = await self._get_processor(bot_phrases=bot_phrases, process=state.process_name)
        except exceptions.ProcessHandlerNotFound:
            logger.warning(
                f'Handler for query "{query.id}" not found. '
                + f'Chat id {query.message.chat.id}. User {query.from_user.full_name}',
            )
            return

        await processor.process(
            message=None,
            query=query,
            bot_phrases=bot_phrases,
            internal_user=internal_user,
        )

        new_state = self.state_controller.get_state(query.message.chat.id)
        if new_state and new_state.is_complete:
            await self._update_messages(query.message.chat.id, query.bot)
            self.state_controller.delete_state(state.chat_id)

    async def _get_processor(
        self,
        bot_phrases: BotPhrases,
        process: str | None,
        message: str | None = None,
    ) -> processors.BaseProcessor:
        match process or message:
            case ProcessName.REGISTRATION.value | bot_phrases.registrate_btn:
                return self.registration_processor
            case ProcessName.TEAM_CHOOSING.value | bot_phrases.generate_teams_btn:
                return self.team_choosing_process
            case _:
                obj_description = f'process "{process}"' if process else f'message "{message}"'
                raise exceptions.ProcessHandlerNotFound(f'Handler for {obj_description} not found.')

    async def _update_messages(self, chat_id: int, bot: Bot) -> None:
        state = self.state_controller.get_state(chat_id)
        if state is None:
            return

        updated_messages = []
        for message_id, msg_new_data in state.messages_to_update.items():
            try:
                msg_id = await self._update_message_impl(state, bot, msg_new_data)
            except TelegramBadRequest:
                continue

            if msg_id is not None:
                updated_messages.append(message_id)

        self.state_controller.remove_messages_from_update(state.chat_id, *updated_messages)

    @async_log(lvl=LOWEST_LOG_LVL)
    async def _update_message_impl(
        self,
        state: StateModel,
        bot: Bot,
        msg_new_data: MessageNewData,
    ) -> int | None:
        """Edit messages related to the process and return id if updated."""
        if msg_new_data.update_on_completion_only and not state.is_complete:
            return

        if msg_new_data.remove:
            await bot.delete_message(chat_id=state.chat_id, message_id=msg_new_data.message_id)
            return

        if msg_new_data.remove_markup:
            await bot.edit_message_reply_markup(
                chat_id=state.chat_id,
                message_id=msg_new_data.message_id,
                reply_markup=None,
            )

        if msg_new_data.text is not None:
            await bot.edit_message_text(
                chat_id=state.chat_id,
                message_id=msg_new_data.message_id,
                text=msg_new_data.text,
            )

        return msg_new_data.message_id


@lru_cache()
def get_bot_controller() -> BotController:
    """Create and return Bot Controller."""
    return BotController(telegram_bot)

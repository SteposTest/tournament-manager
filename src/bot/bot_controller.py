import logging
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
        self.create_tournament_process = processors.BaseProcessor(self.state_controller)
        self.base_processor = processors.BaseProcessor(self.state_controller)

    async def pass_message_to_processor(self, message: Message, query: CallbackQuery | None = None):
        """Find a processor and send a message to it."""
        telegram_user = query.from_user if query else message.from_user
        internal_user, bot_phrases = await get_internal_user_with_language_pack(telegram_user)

        state = self.state_controller.get_state(message.chat.id)
        if state is not None and state.is_query and query is None:
            await message.answer(random.choice(bot_phrases.wrong_msg))
            return

        process = state.process_name if state else None
        try:
            processor = await self._get_processor(bot_phrases=bot_phrases, process=process, message=message)
        except exceptions.ProcessHandlerNotFound:
            await message.answer(random.choice(bot_phrases.wrong_msg))
            return

        try:
            await async_log(lvl=logging.DEBUG, enable_return_log=False)(processor.process)(
                message=message,
                query=query,
                bot_phrases=bot_phrases,
                internal_user=internal_user,
            )
        except Exception as e:
            logger.exception(f'Exception while processing: {e}')

        new_state = self.state_controller.get_state(message.chat.id)
        if new_state and new_state.is_complete:
            await self._update_messages_from_state(message.chat.id, message.bot)
            self.state_controller.delete_state(new_state.chat_id)

    @async_log(lvl=LOWEST_LOG_LVL)
    async def _get_processor(
        self,
        bot_phrases: BotPhrases,
        process: str | None,
        message: Message | None = None,
    ) -> processors.BaseProcessor:
        match process or message.text:
            case ProcessName.REGISTRATION.value | bot_phrases.registrate_btn:
                return self.registration_processor
            case ProcessName.TEAM_CHOOSING.value | bot_phrases.generate_teams_btn:
                return self.team_choosing_process
            case ProcessName.CREATE_TOURNAMENT.value | bot_phrases.create_tournament_btn:
                return self.create_tournament_process
            case bot_phrases.get_site_link_btn:
                return self.base_processor
            case _:
                payload = f'process "{process}"' if process else f'message "{message.text}"'
                raise exceptions.ProcessHandlerNotFound(
                    f'Handler for {payload} not found.'
                    + f'Chat id {message.chat.id}. User {message.from_user.full_name}',
                )

    async def _update_messages_from_state(self, chat_id: int, bot: Bot) -> None:
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

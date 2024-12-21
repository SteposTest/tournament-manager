import random
from functools import lru_cache

from aiogram.client.bot import Bot
from aiogram.types import Message, CallbackQuery

from src.bot import exceptions
from src.bot import processors
from src.bot.models import ProcessName
from src.bot.state_controller import StateController
from src.bot.utils import get_internal_user_with_language_pack
from src.language.models import BotPhrases
from src.runner import telegram_bot
from src.utils.log import get_logger

logger = get_logger(__name__)


class BotController:
    """Processing of all bot operations."""

    def __init__(self, bot: Bot):
        self.bot = bot

        self.state_controller = StateController()

        self.registration_processor = processors.RegistrationProcessor(self.state_controller)

    async def pass_message_to_processor(self, message: Message) -> None:
        """Find a processor and send a message to it."""
        internal_user, bot_phrases = await get_internal_user_with_language_pack(message.from_user)
        state = self.state_controller.get_state(message.chat.id)
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

        new_state = self.state_controller.get_state(state.chat_id)
        if new_state and new_state.is_complete:
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
            raise exceptions.QueryHandlerNotFound(
                f'Handler for query "{query.id}" not found. '
                + f'Chat id {query.message.chat.id}. User {query.from_user.full_name}',
            )

        await processor.process(
            message=None,
            query=query,
            bot_phrases=bot_phrases,
            internal_user=internal_user,
        )

        new_state = self.state_controller.get_state(state.chat_id)
        if new_state and new_state.is_complete:
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
            case _:
                obj_description = f'process "{process}"' if process else f'message "{message}"'
                raise exceptions.ProcessHandlerNotFound(f'Handler for {obj_description} not found.')

    async def _update_messages(self, chat_id: int, bot: Bot) -> None:
        """Edit messages related to the process."""
        state = self.state_controller.get_state(chat_id)
        if state is None:
            return

        updated_messages = []
        for message_id, msg_new_data in state.messages_to_update.items():
            if msg_new_data.update_on_completion_only and not state.is_complete:
                continue

            if msg_new_data.remove:
                await bot.delete_message(chat_id=state.chat_id, message_id=message_id)
                updated_messages.append(message_id)
                continue

            await bot.edit_message_reply_markup(
                chat_id=state.chat_id,
                message_id=message_id,
                reply_markup=msg_new_data.inline_markup,
            )

            if msg_new_data.text is not None:
                await bot.edit_message_text(
                    chat_id=state.chat_id,
                    message_id=message_id,
                    text=msg_new_data.text,
                )

            updated_messages.append(message_id)

        self.state_controller.remove_messages_from_update(state.chat_id, *updated_messages)


@lru_cache()
def get_bot_controller() -> BotController:
    """Create and return Bot Controller."""
    return BotController(telegram_bot)

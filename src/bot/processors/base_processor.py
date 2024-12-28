from aiogram.types import Message, CallbackQuery

from src.apps.manager.models import CustomUser as InternalUser
from src.bot.models import ProcessName
from src.bot.state_controller import StateController
from src.language.models import BotPhrases


class BaseProcessor:
    """Interface of bot action processor."""

    process_name: ProcessName = ProcessName.BASE_PROCESS

    def __init__(self, state_controller: StateController):
        self.state_controller = state_controller

    async def process(
        self,
        message: Message | None,
        query: CallbackQuery | None,
        bot_phrases: BotPhrases,
        internal_user: InternalUser | None,
    ) -> None:
        """The user registration process."""
        await message.answer(bot_phrases.future_processor)

    def __str__(self):
        return f'Process: {self.process_name.value}'

import logging

from aiogram import Router
from aiogram.filters.callback_data import CallbackData

from src.config import settings

router = Router()
logger = logging.getLogger(settings.LOGGER_NAME)


class StartCallback(CallbackData, prefix='start'):
    """Callback for the start command."""

    answer: bool


class RegistrationCallback(CallbackData, prefix='registration'):
    """Registrate user callback."""

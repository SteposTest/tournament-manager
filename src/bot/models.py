from enum import Enum
from typing import Any

from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel


class ProcessName(str, Enum):
    """Processes declaration."""

    REGISTRATION = 'REGISTRATION'


class ProcessPhase(str, Enum):
    """Name of current state."""

    REG_EXPECT_NICKNAME = 'waiting_for_nickname'
    REG_EXPECT_CONFIRM = 'waiting_for_confirm'


class MessageNewData(BaseModel):
    """Model for changing messages."""

    message_id: int
    inline_markup: InlineKeyboardMarkup | None = None
    text: str | None = None
    remove: bool = False
    update_on_completion_only: bool = False


class StateModel(BaseModel):
    """Model of State object."""

    chat_id: int
    process_name: ProcessName
    process_phase: ProcessPhase
    is_query: bool = False
    payload: Any | None = None
    messages_to_update: dict[int, MessageNewData] = {}
    is_complete: bool = False

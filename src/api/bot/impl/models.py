from enum import Enum
from typing import Any

from pydantic import BaseModel


class Process(str, Enum):
    """Processes declaration."""

    REGISTRATION = 'REGISTRATION'


class StateName(str, Enum):
    """Name of current state."""

    REG_EXPECT_NICKNAME = 'waiting_for_nickname'
    REG_EXPECT_CONFIRM = 'waiting_for_confirm'


class StateModel(BaseModel):
    """Model of State object."""

    process: Process
    name: str
    is_query: bool = False
    payload: Any | None = None

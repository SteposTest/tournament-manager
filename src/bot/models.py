from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ProcessName(str, Enum):
    """Processes declaration."""

    REGISTRATION = 'REGISTRATION'
    TEAM_CHOOSING = 'TEAM_CHOOSING'


class ProcessPhase(str, Enum):
    """Name of current state."""

    REG_EXPECT_NICKNAME = 'waiting_for_nickname'
    REG_EXPECT_CONFIRM = 'waiting_for_confirm'

    TC_EXPECT_PLAYERS_COUNT = 'waiting_for_player_count'
    TC_EXPECT_TEAM_RATING = 'waiting_for_team_rating'
    TC_EXPECT_TEAMS_CONFIRM = 'waiting_for_teams_confirm'


class MessageNewData(BaseModel):
    """Model for changing messages."""

    message_id: int
    remove_markup: bool = False
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
    teams_by_filter_ids: list[UUID] | None = None
    messages_to_update: dict[int, MessageNewData] = {}
    is_complete: bool = False

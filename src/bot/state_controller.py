from typing import Any

from src.bot.models import StateModel, MessageNewData, ProcessPhase


class StateController:
    """Interface of State object."""

    def __init__(self) -> None:
        self.state: dict[int, StateModel] = {}

    def create_state(self, chat_id: int, state: StateModel) -> None:
        """Create new state by chat_id."""
        self.state[chat_id] = state

    def get_state(self, chat_id: int) -> StateModel:
        """Return state object by chat_id."""
        return self.state.get(chat_id)

    def update_state(
        self,
        chat_id: int,
        process_phase: ProcessPhase | None = None,
        is_query: bool | None = None,
        payload: Any | None = None,
        is_complete: bool | None = None,
    ) -> None:
        """Update state by chat_id."""
        current_state = self.state.pop(chat_id)
        new_state = StateModel(
            chat_id=chat_id,
            process_name=current_state.process_name,
            process_phase=process_phase if process_phase else current_state.process_phase,
            is_query=is_query if is_query else current_state.is_query,
            payload=payload if payload else current_state.payload,
            messages_to_update=current_state.messages_to_update,
            is_complete=is_complete if is_complete else current_state.is_complete,
        )

        self.create_state(chat_id, new_state)

    def add_messages_to_update(self, chat_id: int, *data_objects: MessageNewData) -> None:
        """Add MessageNewData objects to messages_to_update."""
        state = self.get_state(chat_id)
        state.messages_to_update.update({new_data.message_id: new_data for new_data in data_objects})

    def remove_messages_from_update(self, chat_id: int, *messages_ids: int) -> None:
        """Remove MessageNewData objects from messages_to_update."""
        state = self.get_state(chat_id)
        for message_id in messages_ids:
            state.messages_to_update.pop(message_id)

    def delete_state(self, chat_id: int) -> None:
        """Delete state by chat_id."""
        self.state.pop(chat_id)

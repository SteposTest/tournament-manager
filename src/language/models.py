from pydantic import BaseModel


class BotPhrases(BaseModel):
    """Phrases that the bot responds to users with."""

    user_not_found: str

    reg_msg_answer_yes: str
    reg_msg_answer_no: str
    reg_done: str
    reg_reject: str


class BotRepresentation(BaseModel):
    """Description of the bot commands."""

    short_description: str
    description: str

    start: str
    registrate: str

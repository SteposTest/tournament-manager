from pydantic import BaseModel


class BotPhrases(BaseModel):
    """Phrases that the bot responds to users with."""

    reg_msg: str
    reg_msg_answer_yes: str
    reg_msg_answer_no: str
    reg_done: str
    reg_reject: str


class BotCommandsDescription(BaseModel):
    """Description of the bot commands."""

    start: str

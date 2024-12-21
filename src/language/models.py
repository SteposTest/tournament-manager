from pydantic import BaseModel


class BotPhrases(BaseModel):
    """Phrases that the bot responds to users with."""

    yes_btn: str
    no_btn: str
    wrong_btn_pressing: str
    wrong_msg: list[str]

    welcome_msg: str
    user_not_found: str

    input_field_placeholder: str
    registrate_btn: str
    generate_teams_btn: str
    create_tournament_btn: str
    get_team_btn: str
    get_tournament_table_btn: str
    get_last_games_btn: str
    get_future_games_btn: str
    get_site_link: str

    reg_nickname_request: str
    reg_nickname_request_again: str
    reg_nickname_in_use: str
    reg_nickname_confirm: str
    reg_reject_btn: str
    reg_reject: str
    reg_done: str
    reg_after: str


class BotRepresentation(BaseModel):
    """Description of the bot commands."""

    short_description: str
    description: str

    start: str

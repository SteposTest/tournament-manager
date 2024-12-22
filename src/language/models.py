from pydantic import BaseModel


class BotPhrases(BaseModel):
    """Phrases that the bot responds to users with."""

    yes_btn: str
    no_btn: str
    wrong_btn_pressing: str
    wrong_msg: list[str]

    welcome_msg: str
    user_not_found: str
    answer: str
    unknown: str
    team_description: str

    input_field_placeholder: str
    registrate_btn: str
    generate_teams_btn: str
    create_tournament_btn: str
    get_team_btn: str
    get_tournament_table_btn: str
    get_last_games_btn: str
    get_future_games_btn: str
    get_site_link_btn: str

    reg_nickname_request: str
    reg_nickname_request_again: str
    reg_nickname_in_use: str
    reg_nickname_confirm: str
    reg_reject_btn: str
    reg_reject: str
    reg_done: str
    reg_after: str

    tc_players_count_request: str
    tc_is_teams_country_needed: str
    tc_teams_country_request: str
    tc_rating_request: str
    tc_teams_country_nvrmind_btn: str
    tc_teams_country: str
    tc_change_team_btn: str
    tc_teams_confirm_question: str
    tc_updating_is_unavailable: str
    tc_done: str
    tc_first_round_pairs: str


class BotRepresentation(BaseModel):
    """Description of the bot commands."""

    short_description: str
    description: str

    start: str

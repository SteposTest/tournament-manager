from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, User as TelegramUser

from src.apps.manager.models import CustomUser as InternalUser
from src.language.manager import get_bot_phrases
from src.language.models import BotPhrases


async def build_main_reply_keyboard(internal_user: InternalUser | None, bot_phrases: BotPhrases) -> ReplyKeyboardMarkup:
    """Generate main reply keyboard with base bot functionality."""
    registration_btn = KeyboardButton(text=bot_phrases.registrate_btn)
    generate_teams_btn = KeyboardButton(text=bot_phrases.generate_teams_btn)
    create_tournament_btn = KeyboardButton(text=bot_phrases.create_tournament_btn)
    get_team_btn = KeyboardButton(text=bot_phrases.get_team_btn)
    get_tournament_table_btn = KeyboardButton(text=bot_phrases.get_tournament_table_btn)
    get_last_games_btn = KeyboardButton(text=bot_phrases.get_last_games_btn)
    get_future_games_btn = KeyboardButton(text=bot_phrases.get_future_games_btn)
    get_site_link = KeyboardButton(text=bot_phrases.get_site_link_btn)

    all_buttons = [generate_teams_btn]
    if internal_user is not None:
        all_buttons.extend(
            [
                create_tournament_btn,
                get_site_link,
            ],
        )

        is_there_are_active_tournaments = await internal_user.tournaments.filter(is_active=True).aexists()
        if is_there_are_active_tournaments:
            all_buttons.extend(
                [
                    get_team_btn,
                    get_tournament_table_btn,
                    get_last_games_btn,
                    get_future_games_btn,
                ],
            )
    else:
        all_buttons.insert(0, registration_btn)

    return ReplyKeyboardMarkup(
        keyboard=_format_buttons(all_buttons),
        one_time_keyboard=True,
        resize_keyboard=True,
        input_field_placeholder=bot_phrases.input_field_placeholder,
    )


def digit_to_emoji(number: int) -> str:
    """Format numbers to emoji."""
    emoji = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣',
    }
    return ''.join(emoji.get(digit) for digit in str(number))


async def get_internal_user_with_language_pack(telegram_user: TelegramUser) -> tuple[InternalUser, BotPhrases]:
    """Find and return InternalUser and BotPhrases."""
    bot_phrases = get_bot_phrases(telegram_user.language_code)
    internal_user = await InternalUser.objects.filter(telegram_username=telegram_user.username).afirst()
    return internal_user, bot_phrases


def _format_buttons(all_buttons: list[KeyboardButton]) -> list[list[KeyboardButton]]:
    formated_buttons = []
    while all_buttons:
        buttons_line = all_buttons[:2]
        for btn in buttons_line:
            all_buttons.remove(btn)

        formated_buttons.append(buttons_line)

    return formated_buttons

import random

from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.apps.manager.models import CustomUser as InternalUser
from src.apps.manager.models import Team
from src.bot.callbacks import NumericCallback
from src.bot.models import ProcessPhase, StateModel, ProcessName, MessageNewData
from src.bot.processors.base_processor import BaseProcessor
from src.bot.utils import build_main_reply_keyboard
from src.language.models import BotPhrases
from src.utils.enums import Country


class TeamChoosingProcessor(BaseProcessor):
    """Team choosing processor."""

    process_name = ProcessName.TEAM_CHOOSING
    max_players_count = 10

    async def process(
        self,
        message: Message | None,
        query: CallbackQuery | None,
        bot_phrases: BotPhrases,
        internal_user: InternalUser,
    ) -> None:
        """Process message."""
        chat_id = message.chat.id if message else query.message.chat.id
        state = self.state_controller.get_state(chat_id)
        if state is None:
            builder = InlineKeyboardBuilder()

            for i in range(1, self.max_players_count + 1):
                builder.button(
                    text=str(i),
                    callback_data=NumericCallback(answer=i).pack(),
                )
            builder.adjust(2)

            teams_count_msg = await message.answer(
                text=bot_phrases.tc_players_count_request,
                reply_markup=builder.as_markup(),
            )

            self.state_controller.create_state(
                chat_id=chat_id,
                state=StateModel(
                    chat_id=chat_id,
                    is_query=True,
                    process_name=self.process_name,
                    process_phase=ProcessPhase.TC_EXPECT_PLAYERS_COUNT,
                ),
            )
            self.state_controller.add_messages_to_update(
                chat_id,
                MessageNewData(
                    message_id=teams_count_msg.message_id,
                    remove_markup=True,
                ),
            )
            return

        match state.process_phase:
            case ProcessPhase.TC_EXPECT_PLAYERS_COUNT:
                builder = InlineKeyboardBuilder()
                all_ratings = [rating / 10.0 for rating in range(5, 55, 5)]
                for rating in all_ratings:
                    builder.button(
                        text=str(rating),
                        callback_data=NumericCallback(answer=rating).pack(),
                    )
                builder.adjust(2)

                teams_score_msg = await query.message.answer(
                    text=bot_phrases.tc_rating_request,
                    reply_markup=builder.as_markup(),
                )

                players_count = query.data.split(':')[1]
                self.state_controller.update_state(
                    chat_id=chat_id,
                    is_query=True,
                    process_phase=ProcessPhase.TC_EXPECT_TEAM_RATING,
                    payload=int(players_count),
                )
                self.state_controller.add_messages_to_update(
                    chat_id,
                    MessageNewData(
                        message_id=teams_score_msg.message_id,
                        remove_markup=True,
                    ),
                    MessageNewData(
                        message_id=query.message.message_id,
                        text=f'{query.message.text}\n*{bot_phrases.answer}: {players_count}*',
                    ),
                )
            case ProcessPhase.TC_EXPECT_TEAM_RATING:
                builder = InlineKeyboardBuilder()

                countries = Country.choices(with_unknown=False)
                for country_number, country_name in countries:
                    builder.button(
                        text=country_name.replace('_', ' ').title(),
                        callback_data=NumericCallback(answer=country_number).pack(),
                    )

                builder.button(
                    text=bot_phrases.tc_teams_country_never_mind_btn,
                    callback_data=NumericCallback(answer=1000).pack(),
                )
                builder.adjust(2)

                teams_country_msg = await query.message.answer(
                    text=bot_phrases.tc_teams_country_request,
                    reply_markup=builder.as_markup(),
                )

                teams_rating = query.data.split(':')[1]
                payload = {
                    'players_count': state.payload,
                    'teams_rating': float(teams_rating),
                }

                self.state_controller.update_state(
                    chat_id=chat_id,
                    is_query=True,
                    process_phase=ProcessPhase.TC_EXPECT_TEAM_COUNTRY,
                    payload=payload,
                )
                self.state_controller.add_messages_to_update(
                    chat_id,
                    MessageNewData(
                        message_id=teams_country_msg.message_id,
                        remove_markup=True,
                    ),
                    MessageNewData(
                        message_id=query.message.message_id,
                        text=f'{query.message.text}\n*{bot_phrases.answer}: '
                        f'{teams_rating.replace(".", "\.")}*',  # noqa
                    ),
                )

            case ProcessPhase.TC_EXPECT_TEAM_COUNTRY:
                players_count = state.payload.get('players_count')
                teams_rating = state.payload.get('teams_rating')
                team_country = int(query.data.split(':')[1])

                if team_country == 1000:
                    team_country = None
                else:
                    team_country = Country(team_country)

                await self._send_random_teams(
                    message=query.message,
                    bot_phrases=bot_phrases,
                    players_count=players_count,
                    teams_rating=teams_rating,
                    team_country=team_country,
                )

                await query.message.answer(
                    text=bot_phrases.tc_done,
                    reply_markup=await build_main_reply_keyboard(internal_user, bot_phrases),
                )

                self.state_controller.add_messages_to_update(
                    chat_id,
                    MessageNewData(
                        message_id=query.message.message_id,
                        text=f'{query.message.text}\n*{bot_phrases.answer}: '
                        f'{team_country.value if team_country else bot_phrases.tc_teams_country_never_mind_btn}*',
                    ),
                )

                self.state_controller.update_state(
                    chat_id=chat_id,
                    is_complete=True,
                )

    async def _send_random_teams(
        self,
        message: Message,
        bot_phrases: BotPhrases,
        players_count: int,
        teams_rating: float,
        team_country: Country | None,
    ):
        teams_query = Team.objects.filter(
            rating=teams_rating,
            **({'league__country': team_country} if team_country is not None else {}),
        )

        teams = []
        async for team in teams_query:
            teams.append(team)

        chosen_teams = {player_number: random.choice(teams) for player_number in range(players_count)}

        for player_number, team_object in chosen_teams.items():
            await message.answer(
                text=bot_phrases.team_description.format(
                    player_number=player_number + 1,
                    team_name=team_object.name,
                    general=team_object.general,
                    attack=team_object.attack,
                    midfield=team_object.midfield,
                    defense=team_object.defense,
                ),
                parse_mode='MarkdownV2',
            )

        first_round_pairs = self._generate_first_round_pairs(players_count)
        if first_round_pairs:
            message_text = bot_phrases.tc_first_round_pairs
            for pair in first_round_pairs:
                message_text += f'{pair[0]} - {pair[1]}\n'

            await message.answer(text=message_text)

    @staticmethod
    def _generate_first_round_pairs(players) -> list[tuple[int, int]] | None:
        """Generates pairs for the first round of the game."""
        if players < 2 or players > 10:
            return

        pairs = []
        for i in range(1, players + 1):
            for j in range(1, players + 1):
                if i != j:
                    pairs.append((i, j))
        return pairs

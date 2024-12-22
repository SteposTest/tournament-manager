import random
from uuid import UUID

from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from src.apps.manager.models import Team, CustomUser as InternalUser
from src.apps.manager.utils import get_async_query_result
from src.bot.callbacks import NumericCallback, QuestionCallback
from src.bot.models import ProcessPhase, StateModel, ProcessName, MessageNewData
from src.bot.processors.base_processor import BaseProcessor
from src.bot.utils import build_main_reply_keyboard, digit_to_emoji
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
                all_ratings = [rating / 10.0 for rating in range(50, 0, -5)]
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
                        text=f'{query.message.text}\n<b>{bot_phrases.answer}: {players_count}</b>',
                    ),
                )

            case ProcessPhase.TC_EXPECT_TEAM_RATING:
                teams_rating = query.data.split(':')[1]
                self.state_controller.add_messages_to_update(
                    chat_id,
                    MessageNewData(
                        message_id=query.message.message_id,
                        text=f'{query.message.text}\n<b>{bot_phrases.answer}: {teams_rating}</b>',
                    ),
                )

                teams_ids = await self._send_random_teams(
                    message=query.message,
                    bot_phrases=bot_phrases,
                    players_count=state.payload,
                    teams_rating=float(teams_rating),
                )

                if teams_ids is None:
                    await query.message.answer(text=bot_phrases.tc_updating_is_unavailable)
                    await query.message.answer(
                        text=bot_phrases.tc_done,
                        reply_markup=await build_main_reply_keyboard(internal_user, bot_phrases),
                    )
                    self.state_controller.update_state(
                        chat_id=state.chat_id,
                        is_complete=True,
                    )
                    return

                builder = InlineKeyboardBuilder()
                builder.button(
                    text='✅ ' + bot_phrases.yes_btn + ' ✅',
                    callback_data=QuestionCallback(answer=bot_phrases.yes_btn).pack(),
                )
                is_final_message = await query.message.answer(
                    text=bot_phrases.tc_teams_confirm_question,
                    reply_markup=builder.as_markup(),
                )

                self.state_controller.update_state(
                    chat_id=query.message.chat.id,
                    process_phase=ProcessPhase.TC_EXPECT_TEAMS_CONFIRM,
                    payload=None,
                    teams_by_filter_ids=teams_ids,
                )
                self.state_controller.add_messages_to_update(
                    query.message.chat.id,
                    MessageNewData(
                        message_id=is_final_message.message_id,
                        remove_markup=True,
                        update_on_completion_only=True,
                    ),
                )

            case ProcessPhase.TC_EXPECT_TEAMS_CONFIRM:
                query_answer = query.data.split(':')[1]
                if query_answer == bot_phrases.tc_change_team_btn:
                    player_number = query.message.text.split(':')[0][-2:].strip()

                    teams_ids = state.teams_by_filter_ids
                    team_id = random.choice(teams_ids)
                    teams_ids.remove(team_id)

                    team_obj = await Team.objects.aget(id=team_id)

                    await query.bot.edit_message_text(
                        chat_id=state.chat_id,
                        message_id=query.message.message_id,
                        text=await self._get_team_description(team_obj, bot_phrases, player_number),
                        reply_markup=None,
                    )
                    self.state_controller.remove_messages_from_update(
                        query.message.chat.id,
                        query.message.message_id,
                    )
                if query_answer == bot_phrases.yes_btn:
                    await query.message.answer(
                        text=bot_phrases.tc_done,
                        reply_markup=await build_main_reply_keyboard(internal_user, bot_phrases),
                    )

                    self.state_controller.update_state(
                        chat_id=state.chat_id,
                        is_complete=True,
                    )
                    self.state_controller.add_messages_to_update(
                        state.chat_id,
                        MessageNewData(
                            message_id=query.message.message_id,
                            remove_markup=True,
                        ),
                    )

    async def _send_random_teams(
        self,
        message: Message,
        bot_phrases: BotPhrases,
        players_count: int,
        teams_rating: float,
        team_country: Country | None = None,
    ) -> list[UUID] | None:
        teams_query = Team.objects.filter(
            rating=teams_rating,
            **({'league__country': team_country} if team_country is not None else {}),
        ).values_list('id', flat=True)

        teams_ids = await get_async_query_result(teams_query)

        is_updating_available = (len(teams_ids) / players_count) > 2

        builder = InlineKeyboardBuilder()
        builder.button(
            text=bot_phrases.tc_change_team_btn,
            callback_data=QuestionCallback(answer=bot_phrases.tc_change_team_btn).pack(),
        )

        for player_number in range(1, players_count + 1):
            team_id = random.choice(teams_ids)
            teams_ids.remove(team_id)

            team_object = await Team.objects.aget(id=team_id)
            team_description_message = await message.answer(
                text=await self._get_team_description(team_object, bot_phrases, player_number),
                reply_markup=builder.as_markup() if is_updating_available else None,
            )

            if is_updating_available:
                self.state_controller.add_messages_to_update(
                    message.chat.id,
                    MessageNewData(
                        message_id=team_description_message.message_id,
                        remove_markup=True,
                        update_on_completion_only=True,
                    ),
                )

        first_round_pairs = self._generate_first_round_pairs(players_count)
        if first_round_pairs:
            message_text = bot_phrases.tc_first_round_pairs
            for pair in first_round_pairs:
                message_text += f'{pair[0]} - {pair[1]}\n'

            await message.answer(text=message_text)

        if is_updating_available:
            return teams_ids

    @staticmethod
    async def _get_team_description(team: Team, bot_phrases, player_number: int | str) -> str:
        league_object = await sync_to_async(lambda: team.league)()
        if league_object.country is not None:
            country = Country(league_object.country).get_readable_name()
        else:
            country = bot_phrases.unknown

        return bot_phrases.team_description.format(
            player_number=player_number,
            team_name=team.name,
            league=league_object.name,
            country=country,
            general=digit_to_emoji(team.general),
            attack=digit_to_emoji(team.attack),
            midfield=digit_to_emoji(team.midfield),
            defense=digit_to_emoji(team.defense),
        )

    @staticmethod
    def _generate_first_round_pairs(players_count) -> list[tuple[int, int]] | None:
        """Generates pairs for the first round of the game."""
        if players_count < 2 or players_count > 10:
            return

        pairs = []
        for i in range(1, players_count + 1):
            for j in range(i + 1, players_count + 1):
                pairs.append((i, j))

        random.shuffle(pairs)
        return pairs

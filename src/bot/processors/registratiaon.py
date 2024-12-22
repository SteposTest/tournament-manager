from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.apps.manager.models import CustomUser as InternalUser
from src.bot.callbacks import QuestionCallback
from src.bot.models import ProcessPhase, StateModel, ProcessName, MessageNewData
from src.bot.processors.base_processor import BaseProcessor
from src.bot.utils import build_main_reply_keyboard
from src.language.models import BotPhrases


class RegistrationProcessor(BaseProcessor):
    """Processing of registration."""

    process_name = ProcessName.REGISTRATION

    async def process(
        self,
        message: Message | None,
        query: CallbackQuery | None,
        bot_phrases: BotPhrases,
        internal_user: InternalUser | None,  # noqa
    ) -> None:
        """The user registration process."""
        chat_id = message.chat.id if message else query.message.chat.id
        state = self.state_controller.get_state(chat_id)
        if state is None:
            await message.answer(bot_phrases.reg_nickname_request)
            self.state_controller.create_state(
                chat_id=chat_id,
                state=StateModel(
                    chat_id=chat_id,
                    process_name=self.process_name,
                    process_phase=ProcessPhase.REG_EXPECT_NICKNAME,
                ),
            )
            return

        match state.process_phase:
            case ProcessPhase.REG_EXPECT_NICKNAME:
                potential_nickname = message.text
                is_nickname_in_use = await InternalUser.objects.filter(nickname=potential_nickname).aexists()
                if is_nickname_in_use:
                    await message.answer(bot_phrases.reg_nickname_in_use)
                    return

                builder = InlineKeyboardBuilder()

                builder.button(
                    text=bot_phrases.yes_btn,
                    callback_data=QuestionCallback(answer=bot_phrases.yes_btn).pack(),
                )
                builder.button(
                    text=bot_phrases.no_btn,
                    callback_data=QuestionCallback(answer=bot_phrases.no_btn).pack(),
                )
                builder.adjust(2)

                nickname_confirm_msg = await message.answer(
                    text=bot_phrases.reg_nickname_confirm.format(potential_nickname),
                    reply_markup=builder.as_markup(),
                )

                self.state_controller.update_state(
                    chat_id=chat_id,
                    process_phase=ProcessPhase.REG_EXPECT_CONFIRM,
                    is_query=True,
                    payload=potential_nickname,
                )
                self.state_controller.add_messages_to_update(
                    chat_id,
                    MessageNewData(
                        message_id=nickname_confirm_msg.message_id,
                        remove_markup=True,
                    ),
                )

            case ProcessPhase.REG_EXPECT_CONFIRM:
                potential_nickname = state.payload
                answer = query.data.split(':')[1]
                if answer == bot_phrases.yes_btn:
                    telegram_user = query.from_user
                    new_internal_user = InternalUser(
                        username=telegram_user.full_name,
                        telegram_username=telegram_user.username,
                        nickname=potential_nickname,
                        telegram_user_id=telegram_user.id,
                        telegram_chat_id=query.message.chat.id,
                    )
                    await new_internal_user.asave()

                    await query.bot.send_message(
                        chat_id=new_internal_user.telegram_chat_id,
                        text=bot_phrases.reg_done,
                    )
                    await query.bot.send_message(
                        chat_id=new_internal_user.telegram_chat_id,
                        text=bot_phrases.reg_after,
                        reply_markup=await build_main_reply_keyboard(new_internal_user, bot_phrases),
                    )
                    self.state_controller.update_state(chat_id=chat_id, is_complete=True)
                elif answer == bot_phrases.no_btn:
                    self.state_controller.update_state(
                        chat_id=chat_id,
                        process_phase=ProcessPhase.REG_EXPECT_NICKNAME,
                        is_query=True,
                    )
                    await query.message.answer(bot_phrases.reg_nickname_request_again)
                    return

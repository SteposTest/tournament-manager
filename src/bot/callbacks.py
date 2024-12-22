from aiogram.filters.callback_data import CallbackData


class QuestionCallback(CallbackData, prefix='question'):
    """Main callback for yes/no questions."""

    answer: str


class NumericCallback(CallbackData, prefix='number'):
    """Main callback for yes/no questions."""

    answer: int | float

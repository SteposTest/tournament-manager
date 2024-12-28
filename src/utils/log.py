import inspect
import logging
import re
import time
from copy import deepcopy
from types import FunctionType
from typing import Any, Callable, Iterable
from uuid import uuid1
from aiogram.types import Message, CallbackQuery

import ujson
from wrapt import decorator

from src.config import settings

HIDDEN_VALUE = 'hidden'

DEFAULT_SELF_INDICATOR = 'object at'

LOWEST_LOG_LVL = 5


def get_logger(logger_name: str = settings.VERBOSE_LOGGER_NAME) -> logging.Logger:
    """Get logger with specified name with disabled propagation to avoid several log records related to one event."""
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    return logger


def async_log(
    logger_inst: logging.Logger = get_logger(),
    lvl: int = logging.INFO,
    hide_output: bool = False,
    enable_return_log: bool = True,
    hidden_params: Iterable = (),
) -> Callable:
    """
    Decorator to trace function calls in logs.

    It logs function call, function return and any exceptions with separate log records.
    This high-level function is needed to pass additional parameters and customise _log behavior.
    """

    @decorator
    async def _log(wrapped: FunctionType, instance: Any, args: tuple[Any], kwargs: dict[str, Any]) -> Any:
        """Actual implementation of the above decorator."""
        func_name = wrapped.__qualname__
        function_full_name = f'{wrapped.__module__}.{func_name}'
        extra = {
            'call_id': uuid1().hex,
            'function': func_name,
            'function_full_name': function_full_name,
        }

        try:
            params = inspect.getfullargspec(wrapped)
            start_time = time.time()
            extra['input_data'] = get_logged_args(
                params,
                [instance] + list(args) if instance else args,
                kwargs,
                hidden_params,
            )

            logger_inst.log(
                level=lvl,
                msg=f'call {func_name}',
                extra=extra,
            )

            result = await wrapped(*args, **kwargs)

            if not enable_return_log:
                return result

            extra['result'] = HIDDEN_VALUE if hide_output else normalize_for_log(result)
            extra['execution_time_ms'] = int((time.time() - start_time) * 1000)

            logger_inst.log(level=lvl, msg=f'return {func_name}', extra=extra)

            return result
        except Exception as e:
            logger_inst.exception(f'error in {func_name}', extra=extra if extra is not None else {})

            if hasattr(e, 'return_value'):
                return e.return_value

            raise e

    return _log


# fmt: off
def get_logged_args(
    params: inspect.FullArgSpec,
    args: tuple[Any],
    kwargs: dict[str, Any],
    hidden_params: Iterable,
) -> dict[str, Any]:
    """Return dict with function call argument names and their values casted to primitive types."""
    result = {}

    for i, v in enumerate(args[:len(params.args)]):
        arg_name = params.args[i]
        arg_value = _hide_items(v, arg_name, hidden_params)
        result[arg_name] = normalize_for_log(arg_value)

    varargs = params.varargs
    if varargs:
        if _hide_items(args[len(params.args):], varargs, hidden_params) == HIDDEN_VALUE:
            result['*args'] = f'hidden {len(args) - len(params.args)} args'
        else:
            result['*args'] = tuple(normalize_for_log(i) for i in args[len(params.args):])

    for k, v in kwargs.items():
        kwarg = _hide_items(v, k, hidden_params)
        result[k] = normalize_for_log(kwarg)

    self_argument = result.get('self')
    if self_argument is not None:
        result['self'] = _format_self_argument(self_argument)

    return result
# fmt: on


def normalize_for_log(value: Any) -> Any:
    """Cast any value to a primitive type."""
    if isinstance(value, bool) or value is None:
        return str(value)
    elif isinstance(value, dict):
        return {k: normalize_for_log(v) for k, v in value.items()}
    elif isinstance(value, (list, set, frozenset, tuple)):
        return type(value)(normalize_for_log(i) for i in value)
    elif isinstance(value, Message):
        return f'Message id {value.message_id} from {value.from_user.username}: {value.text[:15]}...'
    elif isinstance(value, CallbackQuery):
        return f'CallbackQuery id {value.id} from {value.from_user.username}: {value.data.split(':')[1]}'

    return _get_log_repr(value)


def _get_log_repr(value: Any) -> Any:
    """Cast value of complex type to a primitive type."""
    if inspect.isclass(value):
        return str(value)

    has_log_id = hasattr(value, 'get_log_id')
    if has_log_id:
        return value.get_log_id()

    try:
        ujson.dumps(value)
    except TypeError:
        return str(value)

    return value


def _hide_items(item: Any, item_name: str, hidden_params: Iterable) -> Any:
    """Hide items according to configuration."""
    if item_name in hidden_params:
        return HIDDEN_VALUE

    hide_pointers = []

    for i in hidden_params:
        if re.match(item_name, i):
            pointer = i.split('__')[1:]
            if pointer not in hide_pointers:
                hide_pointers.append(pointer)

    if not hide_pointers:
        return item

    result = deepcopy(item)
    for i in hide_pointers:
        try:
            result = _hide_items_impl(result, i)
        except (KeyError, IndexError, TypeError):
            pass

    return result


def _hide_items_impl(item: Any, pointers: list | tuple):
    if item is None:
        return

    pointer = pointers[0]
    if isinstance(item, list):
        pointer = int(pointer)

    if isinstance(item[pointer], (dict, list)) and len(pointers) > 1:
        item[pointer] = _hide_items_impl(item[pointer], pointers[1:])
    else:
        item[pointer] = HIDDEN_VALUE

    return item


def _format_self_argument(self_argument: str) -> str:
    """Format self string for output."""
    if DEFAULT_SELF_INDICATOR not in self_argument:
        return self_argument

    parts = self_argument.split(DEFAULT_SELF_INDICATOR)
    obj_class_name = parts[0].strip().split('.')[-1]
    object_id = parts[-1].strip().replace('>', '')

    return f'{obj_class_name} {DEFAULT_SELF_INDICATOR} {object_id}'

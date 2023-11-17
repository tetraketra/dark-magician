import functools
import inspect
import logging
import traceback
import re
from dataclasses import is_dataclass
from collections import defaultdict
from typing import Any, Callable, ValuesView, KeysView, ItemsView

import numpy as np
import pandas as pd
import tkinter as tk

from settings import *


logging.basicConfig(
    filename = APP_RUNTIME_SETTINGS['log_file'], 
    level = APP_RUNTIME_SETTINGS['log_level'], 
    format = APP_RUNTIME_SETTINGS['log_format']
)


def _add_logging_formatter(val: Any) -> Any:
    to_return = None
    
    if isinstance(val, pd.DataFrame):
        to_return = f"[{val.iloc[0].to_dict()}, ... x{val.shape[0]}]"
    
    elif isinstance(val, (tuple, list, np.ndarray)) and len(val) > 0:
        if is_dataclass(val[0]):
            to_return =  f"[dataclass(" \
                         f"{ {key:_add_logging_formatter(iv) for key, iv in val[0].__dict__.items()} }" \
                         f"), ... x{len(val)}]"
        to_return = f"[{_add_logging_formatter(val[0])}, ... x{len(val)}]"
        
    elif is_dataclass(val):
        to_return = f"dataclass({ {key:_add_logging_formatter(iv) for key, iv in val.__dict__.items()} })"

    elif isinstance(val, defaultdict):
        to_return = f"{ {"...(defaultdict)...":_add_logging_formatter(val.values())} }"

    elif isinstance(val, (ValuesView, KeysView, ItemsView)):
        to_return = f"{ {'...(dictview)...':_add_logging_formatter(list(val))} }"

    elif isinstance(val, pd.Series):
        to_return = f"{val.to_dict()}"

    elif isinstance(val, tk.Variable):
        to_return = f"{val.get()}"
        
    else:
        to_return = str(val) # `str(val)` may error, so it's at the end

    to_return = re.sub(r'\\+', '', to_return)

    return to_return


def add_logging(log_level: int = logging.DEBUG) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            call_args = inspect.getcallargs(func, *args, **kwargs)
            for key, val in call_args.items():
                call_args[key] = _add_logging_formatter(val)

            msg = f"func_call:{func.__name__}(**{call_args})"

            try:
                result = func(*args, **kwargs)
            except Exception as er:
                logging.error(msg=msg + f" => {er}")
                logging.error(msg=f"traceback:\n{traceback.format_exc()}")
                raise Exception

            logging.log(level=log_level, msg=msg + f" => {_add_logging_formatter(result)}")
            return result
        return wrapper
    return decorator


def logged_call(func: Callable, log_level: int = logging.DEBUG, *args, **kwargs) -> Any:
    call_args = inspect.getcallargs(func, *args, **kwargs)
    for key, val in call_args.items():
        call_args[key] = _add_logging_formatter(val)

    msg = f"func_call:{func.__name__}(**{call_args})"

    try:
        result = func(*args, **kwargs)
    except Exception as er:
        logging.error(msg=msg + f" => {er}")
        logging.error(msg=f"traceback:\n{traceback.format_exc()}")
        raise Exception

    logging.log(level=log_level, msg=msg + f" => {_add_logging_formatter(result)}")
    return result
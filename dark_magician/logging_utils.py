import functools
import inspect
import logging
import traceback
from dataclasses import asdict, is_dataclass, make_dataclass
from typing import Any, Callable, Collection

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
    try:
        if isinstance(val, pd.DataFrame):
            return f"[{val.iloc[0].to_dict()}, ... x{val.shape[0]}]"
        
        if isinstance(val, (tuple, list, np.ndarray)) and len(val) > 0:
            if is_dataclass(val[0]):
                return  f"[dataclass({ {key:_add_logging_formatter(iv) for key, iv in val[0].__dict__.items()} }), ... x{len(val)}]"
            return f"[{_add_logging_formatter(val[0])}, ... x{len(val)}]"
            
        if is_dataclass(val):
            return f"dataclass({ {key:_add_logging_formatter(iv) for key, iv in val.__dict__.items()} })"

        if isinstance(val, tk.Variable):
            return f"{val.get()}"

        return str(val)

    except Exception as e:
        return str(val)


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
    msg = f"func_call:{func.__name__}(**{inspect.getcallargs(func, *args, **kwargs)})"

    try:
        result = func(*args, **kwargs)
    except Exception as er:
        logging.error(msg = msg + f" => {er}")
        logging.error(msg = f"traceback:\n{traceback.format_exc()}")
        raise Exception

    result = func(*args, **kwargs)

    logging.log(level = log_level, msg = msg + f" => {result}")
    return result
import functools
import traceback
import inspect
import logging
from typing import Any, Callable
from dataclasses import is_dataclass, asdict
import numpy as np
import pandas as pd

def _add_logging_formatter(val: Any) -> Any:
    try:
        if isinstance(val, pd.DataFrame):
            return f"[{val.iloc[0].to_dict()}, ... x{val.shape[0]}]"
        
        if isinstance(val, np.ndarray):
            length = val.shape[0]
            if val.ndim == 2:
                val = val[0]
            return f"[{*val[:1],}, ... x{length}]"
        
        if isinstance(val, (tuple, list)):
            if len(val) > 0 and is_dataclass(val[0]):
                return f"[{ {key:_add_logging_formatter(iv) for key,iv in asdict(val[0]).items()} }, ... x{len(val)}]"
            return f"[{*val[:1],}, ... x{len(val)}]"
        
        if is_dataclass(val):
            return f"{ {key:_add_logging_formatter(iv) for key,iv in asdict(val).items()} }"

        return f"{val}"

    except:
        return f"NOT_SERIALIZABLE"


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
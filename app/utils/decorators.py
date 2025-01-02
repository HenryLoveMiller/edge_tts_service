# app/utils/decorators.py
from functools import wraps
import asyncio
import logging

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return asyncio.run(f(*args, **kwargs))
        except Exception as e:
            logging.error(f"Exception in {f.__name__}: {e}")
            raise
    return wrapped
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
import logging

import redis


logger = logging.getLogger(__name__)


def ignore_redis_error(default=None):
    """ decorator for ignoring redis.RedisError

    :param default: default return value when RedisError is raised. It also can
                    be callable, which will be used as a factory for creating a
                    default return value.
    """
    def _ignore_redis_error(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except redis.RedisError:
                logger.warn("operation failed on redis", exc_info=True)
                ret = default() if callable(default) else default
                return ret
        return wrapper
    return _ignore_redis_error

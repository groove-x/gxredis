import copy

from .util import is_key_matured


class RedisChannel(object):
    """ Redis channel wrapper: only publish is supported """

    def __init__(self, channel, redis_client=None, key_params=None):
        self._channel = channel
        self._redis_client = redis_client
        self._key_params = key_params or {}
        self._matured = is_key_matured(self._channel, self._key_params)

    def clone(self, **kwargs):
        """ create a copy of myself """
        key = kwargs.get('key', self._channel)
        redis_client = kwargs.get('redis_client', self._redis_client)
        key_params = kwargs.get('key_params', self._key_params)
        return self.__class__(key, redis_client, key_params)

    @property
    def channel(self):
        return self._channel.format(**self._key_params)

    def __repr__(self):
        return '{}(channel="{}", key_params={})'.format(
            self.__class__.__name__, self._channel, self._key_params)

    def __call__(self, **kwargs):
        if not kwargs:
            return self
        key_params = copy.copy(self._key_params)
        key_params.update(kwargs)
        return self.clone(key_params=key_params)

    def is_matured(self):
        """ whether key_params support all parameters in key or not """
        return self._matured

    def publish(self, message):
        return self._redis_client.publish(self.channel, message)

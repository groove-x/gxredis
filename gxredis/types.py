# -*- coding: utf-8 -*-
from __future__ import unicode_literals

""" Define wrappers for each Redis type """
import copy
import functools
import json
from abc import ABCMeta


def _is_key_matured(key, key_params):
    """ key_params provides full information for key or not """
    try:
        key.format(**key_params)
    except KeyError:
        return False
    else:
        return True


class RedisType(object):
    """ Base class of Redis types """

    __metaclass__ = ABCMeta
    SUPPORTED_OPERATIONS = [
        'debug_object', 'delete', 'dump', 'exists', 'expire', 'expireat',
        'move', 'persist', 'pexpire', 'pexpireat', 'pttl', 'rename',
        'renamenx', 'restore', 'ttl', 'type']
    REDIS_TYPE = None

    def __init__(self, key, redis_client=None, key_params=None):
        self._key = key
        self._redis_client = redis_client
        self._key_params = key_params or {}
        self._matured = _is_key_matured(self._key, self._key_params)
        self._configure_attributes()

    def clone(self, **kwargs):
        """ create a copy of myself """
        key = kwargs.get('key', self._key)
        redis_client = kwargs.get('redis_client', self._redis_client)
        key_params = kwargs.get('key_params', self._key_params)
        return self.__class__(key, redis_client, key_params)

    @property
    def key(self):
        return self._key.format(**self._key_params)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '{}(key="{}", key_params={})'.format(
            self.__class__.__name__, self._key, self._key_params)

    def __call__(self, **kwargs):
        if not kwargs:
            return self
        key_params = copy.copy(self._key_params)
        key_params.update(kwargs)
        return self.clone(key_params=key_params)

    def __getattr__(self, name):
        if name in self.SUPPORTED_OPERATIONS:
            # raise useful error if not matured
            raise AttributeError(
                "Not enough keys are provided for redis operation")
        raise AttributeError

    def _configure_attributes(self):
        if self._matured and self._redis_client is not None:
            for operation in self.SUPPORTED_OPERATIONS:
                func = getattr(self._redis_client, operation)
                method = functools.partial(func, self.key)
                # docstring や help を元の関数からコピー
                functools.update_wrapper(method, func)
                setattr(self, operation, method)

    def is_matured(self):
        """ whether key_params support all parameters in key or not """
        return self._matured

    def is_type_consistent(self):
        """ whether type is consistent or not """
        if not self._matured:
            raise RuntimeError(
                "Only matured data is supported for consistency check")
        return self.type() == self.REDIS_TYPE


class RedisString(RedisType):
    """ Redis String type """
    SUPPORTED_OPERATIONS = RedisType.SUPPORTED_OPERATIONS + [
        'append', 'bitcount', 'bitpos', 'decr', 'get', 'getbit', 'getrange',
        'getset', 'incr', 'incrby', 'incrbyfloat', 'lock', 'psetex', 'set',
        'setbit', 'setex', 'setnx', 'setrange', 'strlen', 'substr']
    REDIS_TYPE = b'string'

    def get_json(self):
        """ get and decode as json """
        value = self.get()
        if value is not None:
            return json.loads(value.decode('utf-8'))
        return None

    def set_json(self, value):
        """ encode to json and set to redis """
        value = json.dumps(value, ensure_ascii=False)
        return self.set(value)

    def setex_json(self, seconds, value):
        """ encode to json and setex to redis """
        value = json.dumps(value, ensure_ascii=False)
        return self.setex(seconds, value)


class RedisList(RedisType):
    """ Redis List type """
    SUPPORTED_OPERATIONS = RedisType.SUPPORTED_OPERATIONS + [
        'blpop', 'brpop', 'brpoplpush', 'lindex', 'linsert', 'llen', 'lpop',
        'lpush', 'lpushx', 'lrange', 'lrem', 'lset', 'ltrim', 'rpop',
        'rpoplpush', 'rpush', 'rpushx', 'sort']
    REDIS_TYPE = b'list'

    def lrange_mget(self, start, stop):
        """ mget items by keys obtained by lrange """
        keys = self.lrange(start, stop)
        if not keys:
            return [], []
        return keys, self._redis_client.mget(list(keys))

    def lrange_mget_json(self, start, stop):
        """ mget items by keys obtained by lrange and decode as json """
        keys, values = self.lrange_mget(start, stop)
        items = []
        for x in values:
            if x is not None:
                items.append(json.loads(x.decode('utf-8')))
            else:
                items.append(None)
        return keys, items


class RedisSet(RedisType):
    """ Redis Set type """
    SUPPORTED_OPERATIONS = RedisType.SUPPORTED_OPERATIONS + [
        'sadd', 'scard', 'sdiff', 'sdiffstore', 'sinter', 'sinterstore',
        'sismember', 'smembers', 'smove', 'sort', 'spop', 'srandmember',
        'srem', 'sscan', 'sscan_iter', 'sunion', 'sunionstore']
    REDIS_TYPE = b'set'

    def smembers_mget(self):
        """ mget items by keys obtained by smembers """
        keys = self.smembers()
        if not keys:
            return [], []
        return keys, self._redis_client.mget(list(keys))

    def smembers_mget_json(self):
        """ mget items by keys obtained by smembers and decode as json """
        keys, values = self.smembers_mget()
        items = []
        for x in values:
            if x is not None:
                items.append(json.loads(x.decode('utf-8')))
            else:
                items.append(None)
        return keys, items


class RedisHash(RedisType):
    """ Redis Hash type """
    SUPPORTED_OPERATIONS = RedisType.SUPPORTED_OPERATIONS + [
        'hdel', 'hexists', 'hget', 'hgetall', 'hincrby', 'hincrbyfloat',
        'hkeys', 'hlen', 'hmget', 'hmset', 'hscan', 'hscan_iter', 'hset',
        'hsetnx', 'hvals']
    REDIS_TYPE = b'hash'


class RedisSortedSet(RedisType):
    """ Redis Sorted Set type """
    SUPPORTED_OPERATIONS = RedisType.SUPPORTED_OPERATIONS + [
        'sort', 'zadd', 'zcard', 'zcount', 'zincrby', 'zinterstore',
        'zlexcount', 'zrange', 'zrangebylex', 'zrangebyscore', 'zrank', 'zrem',
        'zremrangebylex', 'zremrangebyrank', 'zremrangebyscore', 'zrevrange',
        'zrevrangebylex', 'zrevrangebyscore', 'zrevrank', 'zscan',
        'zscan_iter', 'zscore', 'zunionstore']
    REDIS_TYPE = b'zset'


# Extended types

# class RedisGeohash(RedisSortedSet):
#     """ Redis Geohash using Scored Set type """
#     SUPPORTED_OPERATIONS = RedisSortedSet.SUPPORTED_OPERATIONS + [
#         'geoadd', 'geodist', 'geohash', 'geopos', 'georadius',
#         'georadiusbymember']


class RedisHyperLogLog(RedisString):
    SUPPORTED_OPERATIONS = RedisString.SUPPORTED_OPERATIONS + [
        'pfadd', 'pfcount', 'pfmerge']

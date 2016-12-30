# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import redis
from nose.tools import ok_, eq_, raises

from gxredis import (
    RedisDao, RedisString, RedisList, RedisHash, RedisSet, RedisSortedSet,
)


HOSTNAME = "localhost"
PORT = 6379
DB = 15


class SampleDao(RedisDao):
    item = RedisString(key="sample")
    item_list = RedisList(key="sample_list")
    item_set = RedisSet(key="sample_set")
    item_hash = RedisHash(key="sample_hash")
    item_zset = RedisSortedSet(key="sample_zset")


class ImmatureDao(RedisDao):
    item = RedisString(key="sample:{item_id}")
    item_list = RedisList(key="sample_list")


def test_dao():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = SampleDao(client)

    dao.item.set("abc")
    eq_(dao.item.get(), b"abc")
    ok_(dao.item.is_type_consistent())

    dao.item_list.lpush("abc")
    ok_(dao.item_list.is_type_consistent())
    dao.item_list.lpop()

    dao.item_set.sadd("abc")
    ok_(dao.item_set.is_type_consistent())
    dao.item_set.srem("abc")

    dao.item_hash.hset('key', 1)
    ok_(dao.item_hash.is_type_consistent())
    dao.item_hash.hdel('key')

    dao.item_zset.zadd(1, 'a')
    ok_(dao.item_zset.is_type_consistent())
    dao.item_zset.zrem('a')


def test_params():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)

    eq_(dao.item(item_id=1).key, "sample:1")
    dao.item(item_id=1).set("xyz")
    eq_(dao.item(item_id=1).get(), b"xyz")
    ok_(dao.item(item_id=1).is_type_consistent())
    dao.item(item_id=1).delete("xyz")


def test_params_provided_by_dao():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client, key_params={"item_id": 1})

    dao.item.set("xyz")
    eq_(dao.item.get(), b"xyz")
    ok_(dao.item.is_type_consistent())
    dao.item.delete()


def test_pipeline():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = SampleDao(client)

    dao.item_list.delete()

    pipe = dao.pipeline()
    pipe.item_list.lpush("a")
    pipe.item_list.lpush("b")
    eq_(dao.item_list.llen(), 0)
    pipe.execute()
    eq_(dao.item_list.llen(), 2)


@raises(AttributeError)
def test_not_matured():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)
    dao.item.get()


@raises(AttributeError)
def test_attribute_error():
    """ Test for RedisType.__getattr__ """
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)
    dao.item.foo


def test_json():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client, key_params={"item_id": 10})

    value = {"hello": "world"}
    dao.item.set_json(value)
    eq_(dao.item.get(), b'{"hello": "world"}')
    eq_(dao.item.get_json(), value)


def test_lrange_mget():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)

    dao.item_list.delete()
    accr1 = dao.item(item_id=1)
    accr2 = dao.item(item_id=2)
    accr1.set("a")
    accr2.set("b")
    dao.item_list.lpush(accr1.key)
    dao.item_list.lpush(accr2.key)
    keys, items = dao.item_list.lrange_mget(0, 100)

    eq_(len(items), 2)
    eq_(keys, [b"sample:2", b"sample:1"])
    eq_(items, [b"b", b"a"])

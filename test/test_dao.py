import pytest as pytest
import redis

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
    assert dao.item.get() == b"abc"
    assert dao.item.is_type_consistent()

    dao.item_list.lpush("abc")
    assert dao.item_list.is_type_consistent()
    dao.item_list.lpop()

    dao.item_set.sadd("abc")
    assert dao.item_set.is_type_consistent()
    dao.item_set.srem("abc")

    dao.item_hash.hset('key', 1)
    assert dao.item_hash.is_type_consistent()
    dao.item_hash.hdel('key')

    dao.item_zset.zadd({'a': 1})
    assert dao.item_zset.is_type_consistent()
    dao.item_zset.zrem('a')


def test_params():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)

    assert dao.item(item_id=1).key == "sample:1"
    dao.item(item_id=1).set("xyz")
    assert dao.item(item_id=1).get() == b"xyz"
    assert dao.item(item_id=1).is_type_consistent()
    dao.item(item_id=1).delete("xyz")


def test_params_provided_by_dao():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client, key_params={"item_id": 1})

    dao.item.set("xyz")
    assert dao.item.get() == b"xyz"
    assert dao.item.is_type_consistent()
    dao.item.delete()


def test_pipeline():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = SampleDao(client)

    dao.item_list.delete()

    pipe = dao.pipeline()
    pipe.item_list.lpush("a")
    pipe.item_list.lpush("b")
    assert dao.item_list.llen() == 0
    pipe.execute()
    assert dao.item_list.llen() == 2


def test_not_matured():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)
    with pytest.raises(AttributeError):
        dao.item.get()


def test_attribute_error():
    """ Test for RedisType.__getattr__ """
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client)
    with pytest.raises(AttributeError):
        _ = dao.item.foo


def test_json():
    client = redis.StrictRedis(HOSTNAME, PORT, DB)
    dao = ImmatureDao(client, key_params={"item_id": 10})

    value = {"hello": "world"}
    dao.item.set_json(value)
    assert dao.item.get() == b'{"hello": "world"}'
    assert dao.item.get_json() == value


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

    assert len(items) == 2
    assert keys, [b"sample:2" == b"sample:1"]
    assert items, [b"b" == b"a"]

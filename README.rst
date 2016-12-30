gxredis
=======

Simple `redis-py <https://redis-py.readthedocs.io/en/latest/>`_ wrapper library


Usage
-----

.. code-block:: pycon

    >>> import redis
    >>> from gxredis import *

    >>> class ItemDao(RedisDao):
    >>>        item = RedisString("device:{device_id}:item:{item_id}")
    >>>        item_list = RedisList("device:{device_id}:list")
    >>>        item_set = RedisSet("device:{device_id}:set")
    >>>        item_hash = RedisHash("device:{device_id}:hash")
    >>>        item_zset = RedisSortedSet("device:{device_id}:zset")

    >>> client = redis.StrictRedis("localhost", 6379, 15)
    >>> dao = ItemDao(client, key_params={"device_id": "GX123"})

    >>> dao.item
    RedisString(key="device:{device_id}:item:{item_id}", key_params={'device_id': 'GX123'})

    >>> dao.item_list
    RedisList(key="device:{device_id}:list", key_params={'device_id': 'GX123'})

    >>> dao.item(item_id=1).set("item01")
    True

    >>> dao.item(item_id=1).get()
    'item01'

    >>> pipe = dao.pipeline()
    >>> accr1 = pipe.item(item_id=1)     # accessor for item01
    >>> accr2 = pipe.item(item_id=2)     # accessor for item02
    >>> accr1.set("item01")
    >>> accr2.set("item02")
    >>> pipe.item_list.rpush(accr1.key)
    >>> pipe.item_list.rpush(accr2.key)
    >>> pipe.execute()

    >>> dao.item_list.lrange(0, 100)
    ['device:GX123:item:1', 'device:GX123:item:2']


LICENSE
-------

- MIT

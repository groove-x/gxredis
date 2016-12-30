# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .types import RedisType


class RedisDao(object):
    """ base class for Redis DAO """

    def __init__(self, redis_client, key_params=None):
        self._key_params = key_params or {}
        self._redis_client = redis_client
        self._set_instance_attributes()

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '{}(key_params={})'.format(
            self.__class__.__name__, self._key_params)

    def pipeline(self):
        """ create a Redis pipeline """
        pipeline = self._redis_client.pipeline()
        members = {key: val.clone(redis_client=pipeline)
                   for key, val in self._members.items()}
        return RedisPipeline(pipeline, members)

    def _set_instance_attributes(self):
        """ set instance attributes using class attributes """
        members = {}
        definitions = self._gather_definitions()
        for key, def_ in definitions.items():
            member = def_.clone(
                redis_client=self._redis_client,
                key_params=self._key_params)
            setattr(self, key, member)
            members[key] = member
        self._members = members

    def _gather_definitions(self):
        """ gather RedisType definitions """
        definitions = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, RedisType):
                definitions[attr_name] = attr
        return definitions


class RedisPipeline(object):
    """ Redis pipeline """

    def __init__(self, pipeline, members):
        self._pipeline = pipeline
        self._set_members(members)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '{}'.format(self.__class__.__name__)

    def _set_members(self, members):
        self._members = members
        for key, val in members.items():
            setattr(self, key, val)

    def execute(self):
        self._pipeline.execute()

import redis
from odoo import _


class RedisService:

    def __init__(self, host, port, db=0, password=None, username=None):
        if not password and not username:
            self.r = redis.Redis(host=host, port=port, db=db)
        else:
            self.r = redis.Redis(host=host, port=port, db=db, password=password, username=username)

    def get(self, key):
        if self.r:
            return self.r.get(key)
        raise ReferenceError(_('Redis object is not initialized'))

    def set(self, key, value):
        if self.r:
            self.r.set(key, value)

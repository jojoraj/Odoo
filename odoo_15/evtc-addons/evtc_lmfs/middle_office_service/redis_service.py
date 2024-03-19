import redis


class RedisService:

    def __init__(self, host, port, db, password=None, username=None):
        self.r = redis.Redis(host=host, port=port, db=db, password=password, username=username)

    def get(self, key):
        if self.r:
            return self.r.get(key)
        raise ReferenceError('Redis object is not initialized')

    def set(self, key, value):
        if self.r:
            self.r.set(key, value)
            return True

    def expire(self, key, time):
        if self.r:
            self.r.expire(key, time)

    def save(self):
        if self.r:
            self.r.save()

    def ping(self):
        if self.r:
            print(self.r.ping())
            print('connected to redis') 

    def is_redis_available(self):
        try:
            self.r.ping()
            print("Successfully connected to redis")
            return True
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            print("Redis connection error!")
            return False
            

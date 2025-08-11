import redis, json
from flask import current_app

class Cache:
    def __init__(self, app=None):
        self.client = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        url = app.config.get('REDIS_URL')
        try:
            self.client = redis.from_url(url) if url else None
        except Exception:
            self.client = None

    def get(self, key):
        if not self.client:
            return None
        v = self.client.get(key)
        return json.loads(v) if v else None

    def set(self, key, value, ttl=None):
        if not self.client:
            return
        self.client.set(key, json.dumps(value), ex=ttl)

    def delete(self, pattern):
        if not self.client:
            return
        for key in self.client.scan_iter(pattern):
            self.client.delete(key)

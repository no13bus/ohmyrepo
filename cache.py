# coding: utf-8
# author: https://github.com/cloverstd
# source code: https://gist.github.com/cloverstd/10712505
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import hashlib
    sha1 = hashlib.sha1
except ImportError:
    import sha
    sha1 = sha.new
import functools
 
 
def cache(expires=7200):
    def _func(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            handler.expires = expires
            return func(handler, *args, **kwargs)
        return wrapper
    return _func
 
 
class CacheMixin(object):
 
    @property
    def cache(self):
        return self.application.cache
 
    def prepare(self):
        super(CacheMixin, self).prepare()
        key = self._generate_key(self.request)
        print(key)
        if self.cache.exists(self._prefix(key)):
            rv = pickle.loads(self.cache.get(self._prefix(key)))
            self.write_cache(rv)
            self.finish()
 
    def _generate_key(self, request):
        key = pickle.dumps((request.path, request.arguments))
        return sha1(key).hexdigest()
 
    def _prefix(self, key):
        return "Cache:%s" % key
 
    def write_cache(self, chunk):
        super(CacheMixin, self).write(chunk)
 
    def write(self, chunk):
        pickled = pickle.dumps(chunk)
        key = self._generate_key(self.request)
        if hasattr(self, "expires"):
            self.cache.set(self._prefix(key), pickled, self.expires)
        else:
            self.cache.set(self._prefix(key), pickled)
        super(CacheMixin, self).write(chunk)
 
 
class CacheBackend(object):
    """
    The base Cache Backend class
    """
 
    def get(self, key):
        raise NotImplementedError
 
    def set(self, key, value, timeout):
        raise NotImplementedError
 
    def delitem(self, key):
        raise NotImplementedError
 
    def exists(self, key):
        raise NotImplementedError
 
 
class RedisCacheBackend(CacheBackend):
 
    def __init__(self, redis_connection, **options):
        self.options = dict(timeout=86400)
        self.options.update(options)
 
        self.redis = redis_connection
 
    def get(self, key):
        if self.exists(key):
            return self.redis.get(key)
 
        return None
 
    def set(self, key, value, timeout=None):
        self.redis.set(key, value)
        if timeout:
            self.redis.expire(key, timeout)
        else:
            self.redis.expire(key, self.options["timeout"])
 
    def delitem(self, key):
 
        self.redis.delete(key)
 
    def exists(self, key):
        print(key)
 
        return bool(self.redis.exists(key))
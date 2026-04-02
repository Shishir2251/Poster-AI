from dotenv import load_dotenv
import redis
import os
load_dotenv()

r = redis.Redis.from_url(os.getenv("REDIS_URL"))

r.set('foo', 'bar')
value = r.get('foo')

print(value)  # Output: b'bar'
print("Redis connection successful, value for 'foo':", value.decode())
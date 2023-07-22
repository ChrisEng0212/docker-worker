
import redis
from pybit import inverse_perpetual, usdt_perpetual
import os

print('RUN META')

try:
    import config
    API_KEY = config.API_KEY
    API_SECRET = config.API_SECRET
    REDIS_PASS = config.REDIS_PASS
    REDIS_IP = config.REDIS_IP
    LOCAL = True
except Exception as e:
    print('GET ENV', e)
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    REDIS_PASS = os.getenv('REDIS_PASS')
    REDIS_IP = os.getenv('REDIS_IP')
    LOCAL = False


r = redis.Redis(
    host=REDIS_IP,
    port=6379,
    password=REDIS_PASS,
    decode_responses=True
    )

session = inverse_perpetual.HTTP(
    endpoint='https://api.bybit.com',
    api_key=API_KEY,
    api_secret=API_SECRET
)

print('REDIS', r, REDIS_IP, REDIS_PASS)
print('API', session, str(session.get_wallet_balance()['result']['BTC']['equity']))

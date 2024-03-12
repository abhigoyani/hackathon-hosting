import redis
from config import REDIS_URL

r = redis.from_url(REDIS_URL)


def black_list_token(token: str):
    r.setex(token, 60*30, 'blacklisted')
    # r.set(token, 'blacklisted', ex=60*30)


def check_blacklist(token: str):
    return r.exists(token)

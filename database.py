import os
from redis import StrictRedis
REDISHOST = os.getenv("REDISHOST")
REDISPORT = os.getenv("REDISPORT")
REDISAUTH = os.getenv("REDISAUTH")
db  = StrictRedis(host=REDISHOST, port=int(REDISPORT), password=REDISAUTH, db=0, decode_responses=True)
from typing import Awaitable, Union
from config.config import (REDIS_HOST, REDIS_PORT)
from redis import Redis
from redis.commands.core import ResponseT

class RedisDB():
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        try:
            self._client = Redis(self.__host, self.__port, decode_responses=True)
        except Exception as e:
            raise(ValueError, e) 
    
    def getSession(self, key: str) -> ResponseT:
        return self._client.get(f'sessions:{key}')
    
    def addSession(self, key: str, value: str) -> ResponseT:
        return self._client.set(f'sessions:{key}', value)
    
    def addConfirmRay(self, rayid:str, code: int, username: str) -> Union[Awaitable[str], str]:
        return self._client.hmset(f"keys:{rayid}", mapping={
            "conf_code": code,
            "username": username
        })
    
    def getConfirmRay(self, rayid:str) -> Union[Awaitable[dict], dict]:
        return self._client.hgetall(f'keys:{rayid}')
    
    def removeConfirmRay(self, rayid: str) -> ResponseT:
        self._client.delete(f"keys:{rayid}")

redisdb = RedisDB(REDIS_HOST, REDIS_PORT)
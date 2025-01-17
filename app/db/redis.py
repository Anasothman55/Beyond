
from redis.asyncio import RedisError
import redis.asyncio as redis
from app.config import settings
from datetime import timedelta
from fastapi import HTTPException, status
from typing import Optional
from app.autils import http_exception


class RedisManager:
  def __init__(self, redis_config: dict):
    """Initialize Redis connection with configuration."""
    self.redis = redis.Redis(
      host=redis_config.get('host'),
      port=redis_config.get('port'),
      password=redis_config.get('password'),
      ssl=redis_config.get('ssl', False)
    )
    
    # Constants for key prefixes and set names
    self.REFRESH_TOKEN_PREFIX = "refresh_token:"
    self.BLACKLIST_SET = "blacklist"
    self.JIT_BLACKLIST_SET = "jit_blacklist"

  async def _get_refresh_token_key(self, user_id: str) -> str:
    """Generate Redis key for refresh token."""
    return f"{self.REFRESH_TOKEN_PREFIX}{user_id}"

  async def _decode_token(self, token: bytes) -> Optional[str]:
    """Safely decode token from bytes to string."""
    if not token:
      return None
    try:
      return token.decode("utf-8")
    except UnicodeDecodeError:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to decode token"
      )
  async def store_refresh_token(self,user_id: str, refresh_token: str, ttl_days: int):
    key = await self._get_refresh_token_key(user_id)
    result =  await self.redis.setex(key,timedelta(days= ttl_days), value=refresh_token)
    if not result:
      http_exception(status_codes = status.HTTP_500_INTERNAL_SERVER, details="An Error in the server")
    return result
  
  async def get_refresh_token(self, user_id: str) -> str:
    key = await self._get_refresh_token_key(user_id)
    stored_token = await self.redis.get(key)
    if not stored_token:
      http_exception(status_codes = status.HTTP_404_NOT_FOUND, details= "Invalid or expired refresh token")
    return await self._decode_token(stored_token)

  async def delete_refresh_token(self, user_id: str):
    key = await self._get_refresh_token_key(user_id)
    result = await self.redis.delete(key)
    if result == 0:
      http_exception(status_codes= status.HTTP_404_NOT_FOUND, details="Refresh token not found")
    return True

  async def blacklist_refresh_token(self,fti: str):
    result = await self.redis.sadd(self.BLACKLIST_SET, fti)
    if not result:
      http_exception(status_codes = status.HTTP_500_INTERNAL_SERVER, details= "An Error in the server")
    return 1

  async def is_token_blacklisted(self,fti):
    try:
      result = await self.redis.sismember(self.BLACKLIST_SET, fti)
      if result:
        http_exception(status_codes=status.HTTP_401_UNAUTHORIZED, details="Refresh token is blacklisted")
      else:
        return 1
    except RedisError as rex:
      http_exception(status_codes= status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(rex))

  async def blacklist_access_token(self,jit: str):
    result = await self.redis.sadd(self.JIT_BLACKLIST_SET, jit)
    if not result:
      http_exception(status_codes = status.HTTP_500_INTERNAL_SERVER, details= "An Error in the server")
    return 1

  async def is_jit_blacklisted(self,jit):
    try:
      result = await self.redis.sismember(self.JIT_BLACKLIST_SET, jit)
      if result:
        http_exception(status_codes = status.HTTP_401_UNAUTHORIZED, details= "Access token is blacklisted")
      else:
        return 1
    except RedisError as rex:
      http_exception(status_codes= status.HTTP_500_INTERNAL_SERVER_ERROR, details="An error in the server")



redis_config = {
  'host': settings.UPSTASH_REDIS_HOST,
  'port': settings.UPSTASH_REDIS_PORT,
  'password': settings.UPSTASH_REDIS_PASSWORD,
  'ssl': settings.UPSTASH_REDIS_SSL
}

# Initialize token manager
token_manager = RedisManager(redis_config)









from functools import reduce
import redis.asyncio as redis
from app.config import settings
from datetime import timedelta
from fastapi import HTTPException, status

r = redis.Redis(
  host=settings.UPSTASH_REDIS_HOST,
  port=settings.UPSTASH_REDIS_PORT,
  password=settings.UPSTASH_REDIS_PASSWORD,
  ssl= settings.UPSTASH_REDIS_SSL
)




async def store_refresh_token(user_id: str, refresh_token: str, ttl_days: int):
  # Store the refresh token in Redis with a TTL (time to live)
  return await r.setex(f"refresh_token:{user_id}", timedelta(days= ttl_days), refresh_token)

async def get_refresh_token(user_id: str) -> str:
  stored_token = await r.get(f"refresh_token:{user_id}")
  if not stored_token:
    return None
  try:
    return stored_token.decode("utf-8")
  except UnicodeDecodeError:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decode refresh token")


async def blacklist_refresh_token(refresh_token: str):
  # Store the refresh token in the blacklist set
  result = await r.sadd("blacklist", refresh_token)
  return result > 0

async def blacklist_access_token(jit: str):
  result = await r.sadd("jit_blacklist", jit)
  return result > 0

async def is_token_jit_blacklisted(jit: str):
  # Check if the JWT ID is in the blacklist set
  return await r.sismember("jit_blacklist", jit)

async def is_token_blacklisted(refresh_token: str) -> bool:
  # Check if the refresh token is in the blacklist set
  return await r.sismember("blacklist", refresh_token)


async def delete_refresh_token(user_id: str, refresh_token: str):
  # Retrieve the stored token for the given user
  key = f"refresh_token:{user_id}"
  stored_token = await r.get(key)
  if not stored_token:
    print("stored_token")
    return False  # Token not found
  # Decode and compare the token values
  if stored_token.decode("utf-8") == refresh_token:
    # Delete the token (the key itself)
    result = await r.delete(key)
    return result > 0

  return False  # Token mismatch
"""
Redis configuration and connection management for caching and message queuing.
"""

import os
import json
import pickle
import hashlib
import asyncio
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis configuration settings"""
    
    def __init__(self):
        # Redis connection settings
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
        
        # Connection pool settings
        self.REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
        self.REDIS_RETRY_ON_TIMEOUT = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
        self.REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
        self.REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        
        # Cache settings
        self.DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
        self.QUESTION_CACHE_TTL = int(os.getenv("QUESTION_CACHE_TTL", "86400"))  # 24 hours
        self.EVALUATION_CACHE_TTL = int(os.getenv("EVALUATION_CACHE_TTL", "7200"))  # 2 hours
        self.PDF_TEXT_CACHE_TTL = int(os.getenv("PDF_TEXT_CACHE_TTL", "604800"))  # 1 week

class RedisManager:
    """Redis connection manager with connection pooling and caching utilities"""
    
    def __init__(self, config: RedisConfig = None):
        self.config = config or RedisConfig()
        self._pool = None
        self._client = None
    
    async def get_client(self) -> redis.Redis:
        """Get or create Redis client with connection pooling"""
        if self._client is None:
            self._pool = redis.ConnectionPool(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                max_connections=self.config.REDIS_MAX_CONNECTIONS,
                retry_on_timeout=self.config.REDIS_RETRY_ON_TIMEOUT,
                socket_timeout=self.config.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=self.config.REDIS_SOCKET_CONNECT_TIMEOUT,
                decode_responses=False  # We'll handle encoding/decoding manually
            )
            self._client = redis.Redis(connection_pool=self._pool)
            logger.info(f"Created Redis client with max_connections={self.config.REDIS_MAX_CONNECTIONS}")
        return self._client
    
    async def close(self):
        """Close Redis connection pool"""
        if self._client:
            await self._client.close()
            logger.info("Closed Redis connection pool")
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        try:
            # Try JSON first for simple data types
            if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
                return json.dumps(data, default=str).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Failed to serialize data: {e}")
            raise
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Failed to deserialize data: {e}")
            raise
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in Redis with optional TTL"""
        try:
            client = await self.get_client()
            serialized_value = self._serialize_data(value)
            
            if ttl:
                result = await client.setex(key, ttl, serialized_value)
            else:
                result = await client.set(key, serialized_value)
            
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            client = await self.get_client()
            data = await client.get(key)
            
            if data is None:
                return None
            
            return self._deserialize_data(data)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            client = await self.get_client()
            result = await client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            client = await self.get_client()
            result = await client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check existence of cache key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for an existing key"""
        try:
            client = await self.get_client()
            result = await client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set TTL for cache key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get TTL for a key (-1 if no TTL, -2 if key doesn't exist)"""
        try:
            client = await self.get_client()
            return await client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for cache key {key}: {e}")
            return -2
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value"""
        try:
            client = await self.get_client()
            return await client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {e}")
            return 0
    
    async def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set a hash in Redis"""
        try:
            client = await self.get_client()
            
            # Serialize all values in the mapping
            serialized_mapping = {
                k: self._serialize_data(v) for k, v in mapping.items()
            }
            
            result = await client.hset(key, mapping=serialized_mapping)
            
            if ttl:
                await client.expire(key, ttl)
            
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set hash {key}: {e}")
            return False
    
    async def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a hash from Redis"""
        try:
            client = await self.get_client()
            data = await client.hgetall(key)
            
            if not data:
                return None
            
            # Deserialize all values
            return {
                k.decode('utf-8'): self._deserialize_data(v)
                for k, v in data.items()
            }
        except Exception as e:
            logger.error(f"Failed to get hash {key}: {e}")
            return None
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            
            if keys:
                deleted = await client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            
            return 0
        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0
    
    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        try:
            client = await self.get_client()
            info = await client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'uptime_in_seconds': info.get('uptime_in_seconds')
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}

# Specialized cache classes for different data types
class QuestionCache:
    """Specialized cache for question generation"""
    
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        self.prefix = "questions"
    
    async def get_questions(self, pdf_hash: str, topic: str, count: int, mode: str) -> Optional[List[Dict]]:
        """Get cached questions"""
        key = self.redis._generate_cache_key(
            self.prefix, pdf_hash, topic or "general", count, mode
        )
        return await self.redis.get(key)
    
    async def cache_questions(self, pdf_hash: str, topic: str, count: int, mode: str, questions: List[Dict]) -> bool:
        """Cache generated questions"""
        key = self.redis._generate_cache_key(
            self.prefix, pdf_hash, topic or "general", count, mode
        )
        return await self.redis.set(key, questions, ttl=self.redis.config.QUESTION_CACHE_TTL)

class EvaluationCache:
    """Specialized cache for answer evaluations"""
    
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        self.prefix = "evaluations"
    
    async def get_evaluation(self, question_hash: str, answer_hash: str, level: str) -> Optional[Dict]:
        """Get cached evaluation"""
        key = self.redis._generate_cache_key(
            self.prefix, question_hash, answer_hash, level
        )
        return await self.redis.get(key)
    
    async def cache_evaluation(self, question_hash: str, answer_hash: str, level: str, evaluation: Dict) -> bool:
        """Cache evaluation result"""
        key = self.redis._generate_cache_key(
            self.prefix, question_hash, answer_hash, level
        )
        return await self.redis.set(key, evaluation, ttl=self.redis.config.EVALUATION_CACHE_TTL)

# Global Redis manager instance
redis_manager = RedisManager()
question_cache = QuestionCache(redis_manager)
evaluation_cache = EvaluationCache(redis_manager)

# Health check function
async def check_redis_health() -> bool:
    """Check if Redis is accessible"""
    try:
        client = await redis_manager.get_client()
        await client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

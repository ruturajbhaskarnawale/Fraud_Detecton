import logging
import json
import time
from typing import Dict, Any, List, Optional
from .redis_client import get_redis_client

logger = logging.getLogger("intelligence_cache")

class IntelligenceCache:
    """
    Real-time Intelligence Layer using Redis.
    Tracks velocity, device reputation, and session state.
    """
    
    @staticmethod
    def track_ip(ip_address: str) -> Dict[str, Any]:
        """Increments IP attempt count and returns current metrics."""
        client = get_redis_client()
        key_count = f"v1:ip:{ip_address}:count"
        key_last = f"v1:ip:{ip_address}:last_seen"
        
        if not client:
            return {"count": 1, "last_seen": time.time()}

        try:
            count = client.incr(key_count)
            client.expire(key_count, 3600) # 1 hour TTL
            
            last_seen = client.getset(key_last, time.time())
            return {
                "count": count,
                "last_seen": float(last_seen) if last_seen else time.time()
            }
        except Exception as e:
            logger.error(f"Redis track_ip error: {e}")
            return {"count": 1, "last_seen": time.time()}

    @staticmethod
    def track_device(device_id: str) -> Dict[str, Any]:
        """Tracks device usage frequency and history."""
        client = get_redis_client()
        key_count = f"v1:device:{device_id}:count"
        key_ts = f"v1:device:{device_id}:last_seen"

        if not client:
            return {"count": 1, "last_seen": time.time()}

        try:
            count = client.incr(key_count)
            client.expire(key_count, 86400 * 7) # 7 days TTL for device tracking
            
            last_seen = client.getset(key_ts, time.time())
            return {
                "count": count,
                "last_seen": float(last_seen) if last_seen else time.time()
            }
        except Exception as e:
            logger.error(f"Redis track_device error: {e}")
            return {"count": 1, "last_seen": time.time()}

    @staticmethod
    def track_velocity(entity_id: str, window_seconds: int = 300) -> int:
        """
        Implements a sliding window velocity check for a specific entity.
        Returns the number of attempts in the last X seconds.
        """
        client = get_redis_client()
        key = f"v1:user:{entity_id}:velocity"
        now = time.time()

        if not client:
            return 1

        try:
            # Use sorted set for sliding window
            pipeline = client.pipeline()
            pipeline.zadd(key, {str(now): now})
            pipeline.zremrangebyscore(key, 0, now - window_seconds)
            pipeline.zcard(key)
            pipeline.expire(key, window_seconds + 60)
            results = pipeline.execute()
            
            return results[2] # Count after cleanup
        except Exception as e:
            logger.error(f"Redis track_velocity error: {e}")
            return 1

    @staticmethod
    def cache_session(session_id: str, data: Dict[str, Any], ttl: int = 1800):
        """Stores temporary session state."""
        client = get_redis_client()
        if not client: return

        try:
            client.setex(f"v1:session:{session_id}", ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Redis cache_session error: {e}")

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        client = get_redis_client()
        if not client: return None

        try:
            data = client.get(f"v1:session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get_session error: {e}")
            return None

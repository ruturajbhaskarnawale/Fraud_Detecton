import redis
import logging
import time
import threading
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger("redis_client")

# ── Config ────────────────────────────────────────────────────────────────────
_RETRY_ATTEMPTS   = 1        # startup retries
_RETRY_DELAY_S    = 2        # seconds between startup retries
_HEARTBEAT_SEC    = 30       # how often the keep-alive thread pings Redis
_RECONNECT_DELAY  = 5        # seconds to wait before reconnect attempt after drop


def _parse_redis_url(url: str):
    """Parse redis://host:port/db  →  (host, port, db)."""
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    db   = int(parsed.path.lstrip("/") or 0)
    return host, port, db


class RedisClient:
    """
    Production-grade, always-on Redis client for Veridex.

    Features
    --------
    • Reads REDIS_URL from core.config.settings (overridable via .env)
    • Startup retry loop  – retries up to 5× before giving up
    • Background keep-alive thread – pings every 30 s; reconnects on drop
    • Graceful fallback – callers receive None when Redis is unavailable
    """

    def __init__(self, host: str = None, port: int = None, db: int = None,
                 max_retries: int = _RETRY_ATTEMPTS,
                 retry_delay: float = _RETRY_DELAY_S):

        # ── Resolve connection params from settings.REDIS_URL ─────────────
        try:
            from backend_v2.core.config import settings
            _h, _p, _d = _parse_redis_url(settings.REDIS_URL)
        except Exception:
            try:
                from core.config import settings
                _h, _p, _d = _parse_redis_url(settings.REDIS_URL)
            except Exception:
                _h, _p, _d = "localhost", 6379, 0

        self.host  = host  if host  is not None else _h
        self.port  = port  if port  is not None else _p
        self.db    = db    if db    is not None else _d

        self._client: Optional[redis.Redis] = None
        self._lock   = threading.Lock()
        self._alive  = True          # controls the keep-alive thread

        # ── Startup: retry loop ───────────────────────────────────────────
        self._connect_with_retry(max_retries, retry_delay)

        # ── Keep-alive: background daemon thread ──────────────────────────
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,          # dies automatically when main process exits
            name="redis-keepalive"
        )
        self._heartbeat_thread.start()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _make_client(self) -> redis.Redis:
        """Build a new redis.Redis instance (does NOT ping)."""
        return redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
            retry_on_timeout=True,
        )

    def _connect_with_retry(self, max_retries: int, delay: float):
        """Try to connect up to *max_retries* times on startup."""
        for attempt in range(1, max_retries + 1):
            try:
                client = self._make_client()
                client.ping()
                with self._lock:
                    self._client = client
                print(f"[REDIS] Connected on {self.host}:{self.port} db={self.db}")
                logger.info("[REDIS] Connected on %s:%s db=%s", self.host, self.port, self.db)
                return
            except Exception as e:
                print(f"[RETRY {attempt}/{max_retries}] Redis not ready: {e}")
                logger.warning(f"Redis connect attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)

        # All retries exhausted – start in degraded mode (no crash)
        print(f"[REDIS] ERROR: Unavailable after {max_retries} attempts. Running in fallback mode.")
        logger.error("Redis unavailable at startup. Fallback mode active.")
        self._client = None

    def _reconnect(self):
        """Single reconnect attempt (used by heartbeat)."""
        try:
            client = self._make_client()
            client.ping()
            with self._lock:
                self._client = client
            print(f"[REDIS] Reconnected on {self.host}:{self.port}")
            logger.info(f"Redis reconnected on {self.host}:{self.port}")
        except Exception as e:
            logger.debug(f"Redis reconnect attempt failed: {e}")

    def _heartbeat_loop(self):
        """
        Background daemon: pings Redis every _HEARTBEAT_SEC seconds.
        If ping fails → marks connection dead → schedules a reconnect.
        """
        while self._alive:
            time.sleep(_HEARTBEAT_SEC)
            try:
                with self._lock:
                    c = self._client
                if c is None:
                    # Was already down — try to come back
                    self._reconnect()
                else:
                    c.ping()   # raises if connection dropped
            except Exception:
                logger.warning("[REDIS] Heartbeat failed - connection lost. Reconnecting...")
                with self._lock:
                    self._client = None
                time.sleep(_RECONNECT_DELAY)
                self._reconnect()

    # ── Public API ────────────────────────────────────────────────────────────

    def get_client(self) -> Optional[redis.Redis]:
        """Return the live Redis client, or None if currently unavailable."""
        with self._lock:
            return self._client

    def is_healthy(self) -> bool:
        try:
            with self._lock:
                c = self._client
            return c is not None and c.ping()
        except Exception:
            return False

    def shutdown(self):
        """Stop the keep-alive thread (call on app teardown)."""
        self._alive = False


# ── Singleton ─────────────────────────────────────────────────────────────────
redis_manager = RedisClient()


def get_redis_client() -> Optional[redis.Redis]:
    """Module-level helper used throughout the codebase."""
    return redis_manager.get_client()

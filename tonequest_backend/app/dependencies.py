import os
import threading
from typing import Optional

from dotenv import load_dotenv

# Load .env from the app directory (same directory as this file)
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

import redis
from redis import exceptions as redis_exceptions
from google.cloud.firestore import Client

from app.firebase_config import db as firestore_client

try:
    import fakeredis
except ImportError:  # pragma: no cover - fakeredis should be installed via requirements
    fakeredis = None


_redis_client: Optional[redis.Redis] = None
_redis_lock = threading.Lock()


def get_db() -> Client:
    """
    Return a Firestore client that has been initialised in ``firebase_config``.
    This ensures we reuse the singleton configured at application startup.
    """
    return firestore_client


def _init_redis_client() -> redis.Redis:
    """
    Create a Redis client using ``REDIS_URL`` when available, otherwise fall
    back to an in-memory fake Redis instance for development and testing.
    """
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        try:
            client.ping()
            return client
        except redis_exceptions.ConnectionError:
            # Intentionally fall back to fakeredis below
            pass

    if fakeredis is None:
        raise RuntimeError(
            "REDIS_URL is not configured and fakeredis is unavailable. "
            "Install fakeredis or configure a Redis instance."
        )

    return fakeredis.FakeStrictRedis(decode_responses=True)


def get_redis() -> redis.Redis:
    """
    Provide a thread-safe singleton Redis client for the application.
    """
    global _redis_client

    if _redis_client is None:
        with _redis_lock:
            if _redis_client is None:
                _redis_client = _init_redis_client()

    return _redis_client

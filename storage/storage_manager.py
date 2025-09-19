"""
Storage Manager for integrated Redis, Postgres, and FAISS storage.
Provides unified interface for hot/cold data and vector similarity search.
"""

import json
import pickle
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psycopg2
    from sqlalchemy import (
        create_engine,
        Column,
        String,
        JSON,
        DateTime,
        Float,
        Integer,
        Text,
    )
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import sessionmaker

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import faiss
    import numpy as np

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from config import get_redis_settings, get_mongo_settings


@dataclass
class StorageConfig:
    """Configuration for storage backends."""

    enable_redis: bool = True
    enable_postgres: bool = True
    enable_vector_index: bool = True
    redis_url: Optional[str] = None
    postgres_url: Optional[str] = None
    vector_dimension: int = 384  # Default embedding dimension
    redis_ttl: int = 3600  # 1 hour default TTL for hot data


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store a value with the given key."""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve a value by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass


class RedisBackend(StorageBackend):
    """Redis backend for hot key-value storage."""

    def __init__(self, config: StorageConfig):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available. Install with: pip install redis")

        self.config = config
        redis_settings = get_redis_settings()
        redis_url = config.redis_url or redis_settings.get(
            "redis_url", "redis://localhost:6379/0"
        )

        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()  # Test connection
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Redis connected successfully to {redis_url}")
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.warning(
                f"Redis connection failed: {e}. Operating in degraded mode."
            )
            self.client = None

    def store(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Store value in Redis with optional TTL."""
        if not self.client:
            return False

        try:
            # Serialize value
            serialized = json.dumps(value) if not isinstance(value, str) else value

            # Set TTL
            ttl = ttl or self.config.redis_ttl

            # Store with TTL
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            self.logger.error(f"Redis store failed for key {key}: {e}")
            return False

    def retrieve(self, key: str) -> Any:
        """Retrieve value from Redis."""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None

            # Try to deserialize as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            self.logger.error(f"Redis retrieve failed for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.client:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception as e:
            self.logger.error(f"Redis delete failed for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            self.logger.error(f"Redis exists check failed for key {key}: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter."""
        if not self.client:
            return None

        try:
            return self.client.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Redis increment failed for key {key}: {e}")
            return None


# SQLAlchemy models for Postgres
if POSTGRES_AVAILABLE:
    Base = declarative_base()

    class SimulationLog(Base):
        __tablename__ = "simulation_logs"

        id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
        game_id = Column(String, index=True)
        play_id = Column(String, index=True)
        timestamp = Column(DateTime)
        event_type = Column(String, index=True)
        data = Column(JSON)

    class ErrorLog(Base):
        __tablename__ = "error_logs"

        id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
        play_context = Column(JSON)
        exception_type = Column(String, index=True)
        exception_message = Column(Text)
        stacktrace = Column(Text)
        timestamp = Column(DateTime)
        severity = Column(String, index=True)

    class PolicyEvaluation(Base):
        __tablename__ = "policy_evaluations"

        id = Column(String, primary_key=True)
        policy_a_id = Column(String, index=True)
        policy_b_id = Column(String, index=True)
        drive_count = Column(Integer)
        outcome_deltas = Column(JSON)
        summary = Column(Text)
        timestamp = Column(DateTime)


class PostgresBackend(StorageBackend):
    """Postgres backend for cold persistent storage."""

    def __init__(self, config: StorageConfig):
        if not POSTGRES_AVAILABLE:
            raise ImportError(
                "Postgres dependencies not available. Install with: pip install psycopg2-binary sqlalchemy"
            )

        self.config = config

        # Use environment variable or default connection string
        postgres_url = config.postgres_url or "postgresql://localhost:5432/nfl_sim"

        try:
            self.engine = create_engine(postgres_url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)

            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Postgres connected successfully")
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.warning(
                f"Postgres connection failed: {e}. Operating without persistent storage."
            )
            self.engine = None
            self.session = None

    def store(
        self, key: str, value: Any, table: str = "simulation_logs", **kwargs
    ) -> bool:
        """Store value in Postgres."""
        if not self.session:
            return False

        try:
            if table == "simulation_logs":
                record = SimulationLog(
                    id=key,
                    game_id=kwargs.get("game_id"),
                    play_id=kwargs.get("play_id"),
                    timestamp=kwargs.get("timestamp"),
                    event_type=kwargs.get("event_type", "simulation"),
                    data=value if isinstance(value, dict) else {"value": value},
                )
            elif table == "error_logs":
                record = ErrorLog(
                    id=key,
                    play_context=kwargs.get("play_context"),
                    exception_type=kwargs.get("exception_type"),
                    exception_message=kwargs.get("exception_message"),
                    stacktrace=kwargs.get("stacktrace"),
                    timestamp=kwargs.get("timestamp"),
                    severity=kwargs.get("severity", "error"),
                )
            else:
                # Generic storage (not recommended for production)
                record = SimulationLog(
                    id=key,
                    data=value if isinstance(value, dict) else {"value": value},
                    event_type=table,
                )

            self.session.add(record)
            self.session.commit()
            return True

        except Exception as e:
            self.logger.error(f"Postgres store failed for key {key}: {e}")
            self.session.rollback()
            return False

    def retrieve(self, key: str, table: str = "simulation_logs") -> Any:
        """Retrieve value from Postgres."""
        if not self.session:
            return None

        try:
            if table == "simulation_logs":
                record = self.session.query(SimulationLog).filter_by(id=key).first()
            elif table == "error_logs":
                record = self.session.query(ErrorLog).filter_by(id=key).first()
            else:
                record = None

            if record:
                if hasattr(record, "data"):
                    return record.data
                else:
                    return asdict(record)
            return None

        except Exception as e:
            self.logger.error(f"Postgres retrieve failed for key {key}: {e}")
            return None

    def delete(self, key: str, table: str = "simulation_logs") -> bool:
        """Delete record from Postgres."""
        if not self.session:
            return False

        try:
            if table == "simulation_logs":
                count = self.session.query(SimulationLog).filter_by(id=key).delete()
            elif table == "error_logs":
                count = self.session.query(ErrorLog).filter_by(id=key).delete()
            else:
                count = 0

            self.session.commit()
            return count > 0

        except Exception as e:
            self.logger.error(f"Postgres delete failed for key {key}: {e}")
            self.session.rollback()
            return False

    def exists(self, key: str, table: str = "simulation_logs") -> bool:
        """Check if record exists in Postgres."""
        if not self.session:
            return False

        try:
            if table == "simulation_logs":
                count = self.session.query(SimulationLog).filter_by(id=key).count()
            elif table == "error_logs":
                count = self.session.query(ErrorLog).filter_by(id=key).count()
            else:
                count = 0

            return count > 0

        except Exception as e:
            self.logger.error(f"Postgres exists check failed for key {key}: {e}")
            return False


class VectorIndex:
    """FAISS-based vector index for similarity search."""

    def __init__(self, config: StorageConfig):
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS not available. Install with: pip install faiss-cpu"
            )

        self.config = config
        self.dimension = config.vector_dimension

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(
            self.dimension
        )  # Inner product for cosine similarity
        self.id_map = {}  # Map from FAISS index to our keys
        self.key_map = {}  # Map from our keys to FAISS index
        self.next_id = 0

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Vector index initialized with dimension {self.dimension}")

    def add_vector(
        self, key: str, vector: np.ndarray, metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a vector to the index."""
        try:
            if vector.shape != (self.dimension,):
                self.logger.error(
                    f"Vector dimension mismatch: expected {self.dimension}, got {vector.shape}"
                )
                return False

            # Normalize vector for cosine similarity
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            # Add to FAISS index
            self.index.add(vector.reshape(1, -1).astype(np.float32))

            # Update mappings
            self.id_map[self.next_id] = {"key": key, "metadata": metadata or {}}
            self.key_map[key] = self.next_id
            self.next_id += 1

            return True

        except Exception as e:
            self.logger.error(f"Failed to add vector for key {key}: {e}")
            return False

    def search_similar(
        self, query_vector: np.ndarray, k: int = 10
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar vectors."""
        try:
            if query_vector.shape != (self.dimension,):
                self.logger.error(
                    f"Query vector dimension mismatch: expected {self.dimension}, got {query_vector.shape}"
                )
                return []

            # Normalize query vector
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector = query_vector / norm

            # Search
            scores, indices = self.index.search(
                query_vector.reshape(1, -1).astype(np.float32), k
            )

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx in self.id_map:
                    item = self.id_map[idx]
                    results.append((item["key"], float(score), item["metadata"]))

            return results

        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []

    def remove_vector(self, key: str) -> bool:
        """Remove a vector from the index (FAISS doesn't support removal, so we'll mark as deleted)."""
        if key in self.key_map:
            idx = self.key_map[key]
            if idx in self.id_map:
                self.id_map[idx]["deleted"] = True
                return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "active_vectors": len(
                [v for v in self.id_map.values() if not v.get("deleted", False)]
            ),
        }


class UnifiedStorageManager:
    """Unified storage manager integrating Redis, Postgres, and FAISS."""

    def __init__(self, config: StorageConfig = None):
        self.config = config or StorageConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize backends
        self.redis = None
        self.postgres = None
        self.vector_index = None

        if self.config.enable_redis and REDIS_AVAILABLE:
            try:
                self.redis = RedisBackend(self.config)
            except Exception as e:
                self.logger.warning(f"Redis initialization failed: {e}")

        if self.config.enable_postgres and POSTGRES_AVAILABLE:
            try:
                self.postgres = PostgresBackend(self.config)
            except Exception as e:
                self.logger.warning(f"Postgres initialization failed: {e}")

        if self.config.enable_vector_index and FAISS_AVAILABLE:
            try:
                self.vector_index = VectorIndex(self.config)
            except Exception as e:
                self.logger.warning(f"Vector index initialization failed: {e}")

    def store_hot(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store in hot storage (Redis)."""
        if self.redis:
            return self.redis.store(key, value, ttl=ttl)
        return False

    def retrieve_hot(self, key: str) -> Any:
        """Retrieve from hot storage (Redis)."""
        if self.redis:
            return self.redis.retrieve(key)
        return None

    def store_cold(self, key: str, value: Any, **kwargs) -> bool:
        """Store in cold storage (Postgres)."""
        if self.postgres:
            return self.postgres.store(key, value, **kwargs)
        return False

    def retrieve_cold(self, key: str, table: str = "simulation_logs") -> Any:
        """Retrieve from cold storage (Postgres)."""
        if self.postgres:
            return self.postgres.retrieve(key, table)
        return None

    def store_with_vector(
        self,
        key: str,
        value: Any,
        vector: np.ndarray,
        metadata: Dict[str, Any] = None,
        store_cold: bool = True,
    ) -> bool:
        """Store value with associated vector for similarity search."""
        success = True

        # Store the value
        if store_cold and self.postgres:
            success &= self.postgres.store(key, value, **metadata or {})

        # Store vector for similarity search
        if self.vector_index:
            success &= self.vector_index.add_vector(key, vector, metadata)

        return success

    def search_similar_plays(
        self, query_vector: np.ndarray, k: int = 10
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar plays using vector similarity."""
        if self.vector_index:
            return self.vector_index.search_similar(query_vector, k)
        return []

    def log_error(self, error_envelope) -> bool:
        """Log an error to persistent storage."""
        if self.postgres:
            return self.postgres.store(
                key=str(uuid.uuid4()),
                value=error_envelope.to_dict(),
                table="error_logs",
                **error_envelope.to_dict(),
            )
        return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics from all storage backends."""
        stats = {
            "redis_available": self.redis is not None,
            "postgres_available": self.postgres is not None,
            "vector_index_available": self.vector_index is not None,
        }

        if self.vector_index:
            stats["vector_index"] = self.vector_index.get_stats()

        return stats

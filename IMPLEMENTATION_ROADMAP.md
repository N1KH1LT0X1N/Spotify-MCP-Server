# 🚀 Spotify MCP Server - Complete Implementation Roadmap
## From Production-Ready to Tech Giant Level

**Total Timeline:** 112 weeks (~2 years)
**Effort:** ~3,000+ development hours
**Goal:** Transform into a world-class music intelligence platform

---

## 📋 Implementation Strategy

### Guiding Principles
1. **Incremental Value:** Each phase delivers usable features
2. **Backward Compatibility:** Never break existing users
3. **Test-Driven:** Maintain >90% code coverage
4. **Documentation-First:** Write docs before code
5. **Measure Everything:** Metrics guide decisions

### Phase Dependencies
```
Phase 1 (Foundation)
    ↓
Phase 2 (Caching) ──→ Phase 3 (Observability) ──→ Phase 4 (Resilience)
    ↓                       ↓                           ↓
Phase 5 (SDK/CLI) ──────→ Phase 6 (Dev Tools) ────────┘
    ↓
Phase 7 (AI/ML) ──→ Phase 8 (Analytics) ──→ Phase 9 (Automation)
    ↓                       ↓                       ↓
Phase 10 (Enterprise) ──→ Phase 11 (Cloud) ──────→ Phase 12 (Real-time)
    ↓
Phase 13 (Plugins) ──→ Phase 14 (Advanced) ──→ Phase 15 (Launch)
```

---

## 🏗️ PHASE 1: Foundation & Infrastructure (Weeks 1-4)

**Goal:** Modernize project structure and tooling
**Dependencies:** None
**Deliverables:** Professional dev environment

### 1.1 Project Restructure (Week 1)

#### Tasks
- [ ] Reorganize codebase into clean architecture
- [ ] Create `infrastructure/`, `domain/`, `application/` layers
- [ ] Separate concerns (API, business logic, MCP protocol)
- [ ] Add dependency injection container

#### New Structure
```
spotify_mcp/
├── domain/                 # Business logic (pure Python)
│   ├── models/            # Pydantic models
│   ├── services/          # Business services
│   └── interfaces/        # Abstract interfaces
├── application/           # Use cases
│   ├── playback/
│   ├── search/
│   └── library/
├── infrastructure/        # External concerns
│   ├── spotify/          # Spotify API client
│   ├── cache/            # Caching implementations
│   ├── database/         # Data persistence
│   └── mcp/              # MCP protocol adapter
├── api/                   # API layer (future REST/GraphQL)
└── config/               # Configuration management
```

#### Implementation Steps
```python
# 1. Create dependency injection container
# src/spotify_mcp/container.py
from dependency_injector import containers, providers
from .infrastructure.spotify import SpotifyClient
from .infrastructure.cache import CacheManager

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    spotify_client = providers.Singleton(
        SpotifyClient,
        client_id=config.spotify.client_id,
        client_secret=config.spotify.client_secret,
    )

    cache_manager = providers.Singleton(
        CacheManager,
        backend=config.cache.backend,
    )
```

#### Success Criteria
- ✅ All imports work without circular dependencies
- ✅ Unit tests pass after restructure
- ✅ Clear separation of concerns
- ✅ Dependency injection working

### 1.2 Configuration Management (Week 1)

#### Tasks
- [ ] Replace .env with proper config management
- [ ] Support multiple environments (dev, staging, prod)
- [ ] Add config validation with Pydantic
- [ ] Secret management integration

#### Implementation
```python
# src/spotify_mcp/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class SpotifySettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str = "http://127.0.0.1:8888/callback"

    model_config = SettingsConfigDict(
        env_prefix="SPOTIFY_",
        env_file=".env",
        env_file_encoding="utf-8"
    )

class CacheSettings(BaseSettings):
    backend: Literal["memory", "redis", "sqlite"] = "memory"
    redis_url: str | None = None
    ttl_default: int = 300  # 5 minutes

    model_config = SettingsConfigDict(env_prefix="CACHE_")

class Settings(BaseSettings):
    environment: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"

    spotify: SpotifySettings = SpotifySettings()
    cache: CacheSettings = CacheSettings()

settings = Settings()
```

#### Configuration Files
```yaml
# config/dev.yaml
environment: dev
log_level: DEBUG

spotify:
  redirect_uri: http://127.0.0.1:8888/callback

cache:
  backend: memory
  ttl_default: 60

# config/prod.yaml
environment: prod
log_level: WARNING

spotify:
  redirect_uri: https://api.your-domain.com/callback

cache:
  backend: redis
  redis_url: ${REDIS_URL}
  ttl_default: 300
```

### 1.3 Logging Infrastructure (Week 2)

#### Tasks
- [ ] Replace print() with structured logging
- [ ] Add correlation IDs
- [ ] JSON log formatting
- [ ] Log rotation and archiving

#### Implementation
```python
# src/spotify_mcp/infrastructure/logging.py
import logging
import json
import uuid
from contextvars import ContextVar
from datetime import datetime

# Thread-safe correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'correlation_id': correlation_id_var.get(),
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)

def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Usage in tools
logger = get_logger(__name__)

def play_track(client, uri: str):
    correlation_id_var.set(str(uuid.uuid4()))
    logger.info("Playing track", extra={"uri": uri})
    try:
        result = client.start_playback(uris=[uri])
        logger.info("Track started successfully")
        return result
    except Exception as e:
        logger.error("Failed to play track", extra={"error": str(e)})
        raise
```

### 1.4 Docker & Containerization (Week 2)

#### Tasks
- [ ] Create optimized Dockerfile
- [ ] Multi-stage build for smaller images
- [ ] Docker Compose for local development
- [ ] Health check endpoints

#### Implementation
```dockerfile
# Dockerfile
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 spotify && \
    chown -R spotify:spotify /app

USER spotify

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

EXPOSE 8000

CMD ["python", "-m", "spotify_mcp.server"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  spotify-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=dev
      - LOG_LEVEL=DEBUG
      - CACHE_BACKEND=redis
      - CACHE_REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - redis
    volumes:
      - ./src:/app/src  # Hot reload in dev
    networks:
      - spotify-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - spotify-network
    volumes:
      - redis-data:/data

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - spotify-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./infrastructure/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - spotify-network

networks:
  spotify-network:
    driver: bridge

volumes:
  redis-data:
  prometheus-data:
  grafana-data:
```

### 1.5 CI/CD Enhancements (Week 3)

#### Tasks
- [ ] Multi-stage GitHub Actions
- [ ] Automated semantic versioning
- [ ] Docker image builds and push
- [ ] Automated changelog generation

#### Implementation
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run tests
        run: poetry run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build-docker:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            your-username/spotify-mcp:latest
            your-username/spotify-mcp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  release:
    needs: build-docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Semantic Release
        uses: cycjimmy/semantic-release-action@v3
        with:
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 1.6 Database Schema Design (Week 3-4)

#### Tasks
- [ ] Design schema for caching and analytics
- [ ] Add SQLAlchemy models
- [ ] Create Alembic migrations
- [ ] Add database connection pooling

#### Schema Design
```python
# src/spotify_mcp/infrastructure/database/models.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CachedResponse(Base):
    __tablename__ = 'cached_responses'

    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, index=True)
    endpoint = Column(String(100), index=True)
    response_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)
    hit_count = Column(Integer, default=0)

class PlaybackHistory(Base):
    __tablename__ = 'playback_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True)
    track_uri = Column(String(100))
    track_name = Column(String(255))
    artist_name = Column(String(255))
    played_at = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer)
    context_uri = Column(String(255))  # playlist/album

class UserAnalytics(Base):
    __tablename__ = 'user_analytics'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True)
    metric_name = Column(String(100))  # e.g., 'total_listening_time'
    metric_value = Column(Float)
    period = Column(String(20))  # daily, weekly, monthly
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)

class ApiMetrics(Base):
    __tablename__ = 'api_metrics'

    id = Column(Integer, primary_key=True)
    tool_name = Column(String(100), index=True)
    endpoint = Column(String(255))
    latency_ms = Column(Float)
    status_code = Column(Integer)
    cache_hit = Column(Boolean, default=False)
    error_message = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    correlation_id = Column(String(36), index=True)
```

#### Migrations
```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'cached_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cache_key', sa.String(255), nullable=False),
        sa.Column('endpoint', sa.String(100), nullable=True),
        sa.Column('response_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('hit_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cache_key')
    )
    op.create_index('ix_cached_responses_expires_at', 'cached_responses', ['expires_at'])

def downgrade():
    op.drop_table('cached_responses')
```

### 1.7 Testing Infrastructure Enhancement (Week 4)

#### Tasks
- [ ] Add pytest fixtures for common scenarios
- [ ] Create factory patterns for test data
- [ ] Add integration test suite
- [ ] Performance testing framework

#### Implementation
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, MagicMock
from spotify_mcp.container import Container
from spotify_mcp.infrastructure.database import Database

@pytest.fixture
def container():
    """Dependency injection container for tests"""
    container = Container()
    container.config.from_dict({
        'spotify': {
            'client_id': 'test_client_id',
            'client_secret': 'test_secret',
        },
        'cache': {
            'backend': 'memory',
        }
    })
    return container

@pytest.fixture
def mock_spotify_client():
    """Mock Spotify client with common responses"""
    client = Mock()
    client.current_playback.return_value = {
        'item': {
            'id': '123',
            'name': 'Test Track',
            'artists': [{'name': 'Test Artist'}],
        },
        'is_playing': True,
    }
    return client

@pytest.fixture
def db_session():
    """Test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from spotify_mcp.infrastructure.database.models import Base

    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()

# Test factories
class TrackFactory:
    @staticmethod
    def create(track_id='123', name='Test Track'):
        return {
            'id': track_id,
            'name': name,
            'uri': f'spotify:track:{track_id}',
            'artists': [{'name': 'Test Artist', 'id': 'artist123'}],
            'album': {'name': 'Test Album', 'id': 'album123'},
            'duration_ms': 180000,
        }

class PlaylistFactory:
    @staticmethod
    def create(playlist_id='playlist123', name='Test Playlist'):
        return {
            'id': playlist_id,
            'name': name,
            'uri': f'spotify:playlist:{playlist_id}',
            'tracks': {'total': 10},
            'owner': {'id': 'user123'},
        }

# Performance test example
# tests/performance/test_cache_performance.py
import pytest
import time

def test_cache_performance(container):
    """Ensure cache operations are fast"""
    cache = container.cache_manager()

    # Write performance
    start = time.time()
    for i in range(1000):
        cache.set(f'key_{i}', {'data': f'value_{i}'}, ttl=60)
    write_time = time.time() - start

    assert write_time < 1.0, "Cache writes should complete in under 1 second"

    # Read performance
    start = time.time()
    for i in range(1000):
        cache.get(f'key_{i}')
    read_time = time.time() - start

    assert read_time < 0.5, "Cache reads should complete in under 0.5 seconds"
```

---

## ⚡ PHASE 2: Performance & Caching (Weeks 5-8)

**Goal:** 10x performance improvement through intelligent caching
**Dependencies:** Phase 1 (database, config)
**Deliverables:** Multi-tier caching system

### 2.1 Cache Abstraction Layer (Week 5)

#### Tasks
- [ ] Design cache interface
- [ ] Implement memory cache backend
- [ ] Implement Redis cache backend
- [ ] Implement SQLite cache backend
- [ ] Add cache key generation strategy

#### Interface Design
```python
# src/spotify_mcp/infrastructure/cache/interface.py
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import timedelta

class CacheBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in cache with TTL in seconds"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove value from cache"""
        pass

    @abstractmethod
    async def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

    @abstractmethod
    async def get_stats(self) -> dict:
        """Return cache statistics"""
        pass
```

#### Memory Cache Implementation
```python
# src/spotify_mcp/infrastructure/cache/memory.py
import asyncio
from datetime import datetime, timedelta
from collections import OrderedDict
from typing import Any, Optional
import fnmatch

class MemoryCache(CacheBackend):
    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry['expires_at'] < datetime.utcnow():
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry['value']

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        async with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)

            self._cache[key] = {
                'value': value,
                'expires_at': datetime.utcnow() + timedelta(seconds=ttl),
                'created_at': datetime.utcnow(),
            }
            self._cache.move_to_end(key)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self, pattern: str = "*") -> None:
        async with self._lock:
            if pattern == "*":
                self._cache.clear()
            else:
                keys_to_delete = [
                    k for k in self._cache.keys()
                    if fnmatch.fnmatch(k, pattern)
                ]
                for key in keys_to_delete:
                    del self._cache[key]

    async def exists(self, key: str) -> bool:
        return key in self._cache

    async def get_stats(self) -> dict:
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'backend': 'memory',
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f'{hit_rate:.2f}%',
        }
```

#### Redis Cache Implementation
```python
# src/spotify_mcp/infrastructure/cache/redis.py
import redis.asyncio as redis
import json
from typing import Any, Optional

class RedisCache(CacheBackend):
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._client = redis.from_url(url, decode_responses=True)
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        value = await self._client.get(key)
        if value is None:
            self._misses += 1
            return None

        self._hits += 1
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self._client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def clear(self, pattern: str = "*") -> None:
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(
                cursor=cursor,
                match=pattern,
                count=100
            )
            if keys:
                await self._client.delete(*keys)
            if cursor == 0:
                break

    async def exists(self, key: str) -> bool:
        return await self._client.exists(key) > 0

    async def get_stats(self) -> dict:
        info = await self._client.info('stats')
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'backend': 'redis',
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f'{hit_rate:.2f}%',
            'total_connections': info.get('total_connections_received', 0),
            'connected_clients': info.get('connected_clients', 0),
        }

    async def close(self):
        await self._client.close()
```

### 2.2 Smart Caching Strategies (Week 6)

#### TTL Strategy by Data Type
```python
# src/spotify_mcp/infrastructure/cache/strategies.py
from enum import Enum
from typing import Optional

class CacheStrategy(Enum):
    """Different caching strategies based on data type"""

    # Static data (rarely changes)
    TRACK_METADATA = (3600 * 24, "track:")  # 24 hours
    ALBUM_METADATA = (3600 * 24, "album:")
    ARTIST_METADATA = (3600 * 24, "artist:")
    AUDIO_FEATURES = (3600 * 24 * 7, "audio_features:")  # 1 week

    # Semi-static data
    PLAYLIST_METADATA = (300, "playlist:")  # 5 minutes
    USER_LIBRARY = (180, "library:")  # 3 minutes
    SEARCH_RESULTS = (600, "search:")  # 10 minutes

    # Dynamic data
    PLAYBACK_STATE = (10, "playback:")  # 10 seconds
    QUEUE = (30, "queue:")  # 30 seconds
    DEVICES = (60, "devices:")  # 1 minute

    # User data
    USER_PROFILE = (3600, "user:")  # 1 hour
    USER_TOP_ITEMS = (3600 * 6, "top:")  # 6 hours

    def __init__(self, ttl: int, prefix: str):
        self.ttl = ttl
        self.prefix = prefix

class CacheKeyGenerator:
    """Generate consistent cache keys"""

    @staticmethod
    def track(track_id: str) -> str:
        return f"{CacheStrategy.TRACK_METADATA.prefix}{track_id}"

    @staticmethod
    def playlist(playlist_id: str) -> str:
        return f"{CacheStrategy.PLAYLIST_METADATA.prefix}{playlist_id}"

    @staticmethod
    def search(query: str, types: str, limit: int) -> str:
        import hashlib
        key_data = f"{query}:{types}:{limit}"
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{CacheStrategy.SEARCH_RESULTS.prefix}{hash_key}"

    @staticmethod
    def playback_state(user_id: str) -> str:
        return f"{CacheStrategy.PLAYBACK_STATE.prefix}{user_id}"
```

#### Cache Decorator
```python
# src/spotify_mcp/infrastructure/cache/decorators.py
from functools import wraps
import inspect
import json
import hashlib

def cached(strategy: CacheStrategy):
    """Decorator to cache function results"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache from DI container
            cache = kwargs.pop('_cache', None)
            if cache is None:
                return await func(*args, **kwargs)

            # Generate cache key from function args
            cache_key = _generate_cache_key(func, args, kwargs, strategy.prefix)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl=strategy.ttl)

            return result

        return wrapper

    return decorator

def _generate_cache_key(func, args, kwargs, prefix: str) -> str:
    """Generate a unique cache key from function call"""
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()

    # Create deterministic key from arguments
    key_parts = [func.__name__]
    for param_name, param_value in bound.arguments.items():
        if param_name == 'self' or param_name == 'client':
            continue
        key_parts.append(f"{param_name}={param_value}")

    key_string = ":".join(str(p) for p in key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}{key_hash}"

# Usage in tools
@cached(CacheStrategy.TRACK_METADATA)
async def get_track(client, track_id: str, _cache=None):
    """Get track with caching"""
    return client.track(track_id)
```

### 2.3 Cache Invalidation (Week 6)

#### Implementation
```python
# src/spotify_mcp/infrastructure/cache/invalidation.py
from typing import List
import fnmatch

class CacheInvalidator:
    """Handles cache invalidation on mutations"""

    def __init__(self, cache: CacheBackend):
        self._cache = cache

    async def invalidate_playlist(self, playlist_id: str):
        """Invalidate all playlist-related caches"""
        await self._cache.clear(f"playlist:{playlist_id}*")
        await self._cache.clear(f"user:playlists:*")  # User's playlist list

    async def invalidate_library(self, user_id: str):
        """Invalidate user library caches"""
        await self._cache.clear(f"library:{user_id}:*")

    async def invalidate_playback(self, user_id: str):
        """Invalidate playback state"""
        await self._cache.clear(f"playback:{user_id}")
        await self._cache.clear(f"queue:{user_id}")

    async def invalidate_on_save_tracks(self, user_id: str, track_ids: List[str]):
        """Invalidate when user saves tracks"""
        # Invalidate library
        await self.invalidate_library(user_id)

        # Invalidate individual track caches (saved status)
        for track_id in track_ids:
            await self._cache.delete(f"track:{track_id}:saved:{user_id}")

# Integration with tools
async def add_tracks_to_playlist(client, playlist_id: str, track_uris: List[str],
                                  _cache=None, _invalidator=None):
    """Add tracks with cache invalidation"""
    result = client.playlist_add_items(playlist_id, track_uris)

    # Invalidate affected caches
    if _invalidator:
        await _invalidator.invalidate_playlist(playlist_id)

    return result
```

### 2.4 Cache Warming & Preloading (Week 7)

#### Implementation
```python
# src/spotify_mcp/infrastructure/cache/warming.py
import asyncio
from typing import List
import logging

logger = logging.getLogger(__name__)

class CacheWarmer:
    """Pre-populate cache with frequently accessed data"""

    def __init__(self, client, cache: CacheBackend):
        self._client = client
        self._cache = cache

    async def warm_user_data(self, user_id: str):
        """Pre-load common user data"""
        tasks = [
            self._warm_user_profile(user_id),
            self._warm_user_playlists(user_id),
            self._warm_playback_state(user_id),
            self._warm_saved_tracks(user_id),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Cache warming failed for task {i}: {result}")

    async def _warm_user_profile(self, user_id: str):
        """Cache user profile"""
        profile = self._client.current_user()
        cache_key = CacheKeyGenerator.user_profile(user_id)
        await self._cache.set(
            cache_key,
            profile,
            ttl=CacheStrategy.USER_PROFILE.ttl
        )

    async def _warm_user_playlists(self, user_id: str):
        """Cache user's playlists"""
        playlists = self._client.current_user_playlists(limit=50)
        cache_key = f"library:{user_id}:playlists"
        await self._cache.set(
            cache_key,
            playlists,
            ttl=CacheStrategy.PLAYLIST_METADATA.ttl
        )

    async def _warm_playback_state(self, user_id: str):
        """Cache current playback"""
        try:
            playback = self._client.current_playback()
            if playback:
                cache_key = CacheKeyGenerator.playback_state(user_id)
                await self._cache.set(
                    cache_key,
                    playback,
                    ttl=CacheStrategy.PLAYBACK_STATE.ttl
                )
        except Exception:
            pass  # No active playback is normal

    async def _warm_saved_tracks(self, user_id: str):
        """Cache recently saved tracks"""
        tracks = self._client.current_user_saved_tracks(limit=50)
        cache_key = f"library:{user_id}:tracks:recent"
        await self._cache.set(
            cache_key,
            tracks,
            ttl=CacheStrategy.USER_LIBRARY.ttl
        )

    async def warm_popular_tracks(self, track_ids: List[str]):
        """Pre-load frequently accessed tracks"""
        for track_id in track_ids:
            try:
                track = self._client.track(track_id)
                cache_key = CacheKeyGenerator.track(track_id)
                await self._cache.set(
                    cache_key,
                    track,
                    ttl=CacheStrategy.TRACK_METADATA.ttl
                )
            except Exception as e:
                logger.warning(f"Failed to warm track {track_id}: {e}")
```

### 2.5 Performance Testing & Benchmarks (Week 8)

#### Benchmark Suite
```python
# tests/benchmarks/test_cache_performance.py
import pytest
import time
from spotify_mcp.infrastructure.cache import MemoryCache, RedisCache

class TestCachePerformance:
    @pytest.mark.benchmark
    async def test_memory_cache_read_latency(self, benchmark):
        """Memory cache should have <1ms read latency"""
        cache = MemoryCache()
        await cache.set("test_key", {"data": "value"})

        def read():
            return cache.get("test_key")

        result = benchmark(read)
        assert benchmark.stats.mean < 0.001  # <1ms

    @pytest.mark.benchmark
    async def test_redis_cache_throughput(self):
        """Redis should handle 10k ops/sec"""
        cache = RedisCache()

        start = time.time()
        for i in range(10000):
            await cache.set(f"key_{i}", {"value": i}, ttl=60)
        write_time = time.time() - start

        start = time.time()
        for i in range(10000):
            await cache.get(f"key_{i}")
        read_time = time.time() - start

        write_ops_per_sec = 10000 / write_time
        read_ops_per_sec = 10000 / read_time

        assert write_ops_per_sec > 10000
        assert read_ops_per_sec > 10000

    @pytest.mark.benchmark
    async def test_cache_hit_rate(self):
        """Cache should achieve >80% hit rate in typical usage"""
        cache = MemoryCache()

        # Simulate typical access pattern
        popular_keys = [f"popular_{i}" for i in range(10)]
        rare_keys = [f"rare_{i}" for i in range(100)]

        # Pre-populate popular keys
        for key in popular_keys:
            await cache.set(key, {"data": key})

        # Simulate access pattern (80% popular, 20% rare)
        hits = 0
        total = 1000

        for i in range(total):
            if i % 5 == 0:  # 20% rare
                key = rare_keys[i % len(rare_keys)]
            else:  # 80% popular
                key = popular_keys[i % len(popular_keys)]

            if await cache.get(key) is not None:
                hits += 1

        hit_rate = hits / total
        assert hit_rate > 0.8
```

---

## 🔍 PHASE 3: Observability & Monitoring (Weeks 9-12)

**Goal:** Complete visibility into system behavior
**Dependencies:** Phase 1 (logging), Phase 2 (cache)
**Deliverables:** Metrics, tracing, monitoring stack

### 3.1 Metrics Collection (Week 9)

#### Prometheus Integration
```python
# src/spotify_mcp/infrastructure/metrics/prometheus.py
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
import time
from functools import wraps

# Define metrics
tool_requests_total = Counter(
    'spotify_mcp_tool_requests_total',
    'Total tool requests',
    ['tool_name', 'status']
)

tool_latency_seconds = Histogram(
    'spotify_mcp_tool_latency_seconds',
    'Tool execution latency',
    ['tool_name'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

cache_operations_total = Counter(
    'spotify_mcp_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

cache_hit_rate = Gauge(
    'spotify_mcp_cache_hit_rate',
    'Current cache hit rate percentage',
    ['cache_type']
)

active_users = Gauge(
    'spotify_mcp_active_users',
    'Number of active users'
)

spotify_api_errors_total = Counter(
    'spotify_mcp_spotify_api_errors_total',
    'Spotify API errors',
    ['error_type', 'http_status']
)

server_info = Info(
    'spotify_mcp_server',
    'Server information'
)

# Decorator for automatic metrics
def track_metrics(tool_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                latency = time.time() - start_time
                tool_requests_total.labels(tool_name=tool_name, status=status).inc()
                tool_latency_seconds.labels(tool_name=tool_name).observe(latency)

        return wrapper
    return decorator

# Usage
@track_metrics('play')
async def play(client, uri: str):
    return client.start_playback(uris=[uri])
```

#### Metrics Endpoint
```python
# src/spotify_mcp/api/metrics.py
from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.4",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 3.2 Distributed Tracing (Week 10)

#### OpenTelemetry Setup
```python
# src/spotify_mcp/infrastructure/tracing/setup.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(service_name: str = "spotify-mcp-server"):
    """Initialize OpenTelemetry tracing"""

    # Create resource with service info
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.4",
        "deployment.environment": "production",
    })

    # Setup tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter (to Jaeger, Zipkin, etc.)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # Jaeger collector
        insecure=True
    )

    # Add batch processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Auto-instrument libraries
    RequestsInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()

    return trace.get_tracer(__name__)

# Get tracer instance
tracer = setup_tracing()
```

#### Tracing Decorator
```python
# src/spotify_mcp/infrastructure/tracing/decorators.py
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from functools import wraps
import inspect

def traced(span_name: str = None):
    """Decorator to create trace spans"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get function name for span if not provided
            name = span_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(name) as span:
                # Add function arguments as attributes
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)

                for param_name, param_value in bound.arguments.items():
                    if param_name not in ['self', 'client', 'password', 'token']:
                        span.set_attribute(f"arg.{param_name}", str(param_value))

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator

# Usage
@traced(span_name="playback.play_track")
async def play(client, uri: str):
    with tracer.start_as_current_span("spotify.api.start_playback") as span:
        span.set_attribute("track.uri", uri)
        return client.start_playback(uris=[uri])
```

### 3.3 Dashboard Creation (Week 11)

#### Grafana Dashboard (JSON)
```json
{
  "dashboard": {
    "title": "Spotify MCP Server Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(spotify_mcp_tool_requests_total[5m])",
            "legendFormat": "{{tool_name}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Latency (p50, p95, p99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(spotify_mcp_tool_latency_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(spotify_mcp_tool_latency_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(spotify_mcp_tool_latency_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "spotify_mcp_cache_hit_rate",
            "legendFormat": "{{cache_type}}"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(spotify_mcp_tool_requests_total{status=\"error\"}[5m])",
            "legendFormat": "{{tool_name}}"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "spotify_mcp_active_users"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Spotify API Errors",
        "targets": [
          {
            "expr": "rate(spotify_mcp_spotify_api_errors_total[5m])",
            "legendFormat": "{{error_type}}"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Alerting Rules (Week 12)

#### Prometheus Alerts
```yaml
# infrastructure/prometheus/alerts.yml
groups:
  - name: spotify_mcp_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(spotify_mcp_tool_requests_total{status="error"}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(spotify_mcp_tool_latency_seconds_bucket[5m])
          ) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"

      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: spotify_mcp_cache_hit_rate < 50
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Cache hit rate is low"
          description: "Hit rate is {{ $value }}%"

      # Spotify API errors
      - alert: SpotifyAPIDown
        expr: |
          rate(spotify_mcp_spotify_api_errors_total[5m]) > 0.5
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Spotify API experiencing issues"
          description: "High rate of API errors: {{ $value }}/sec"

      # Service down
      - alert: ServiceDown
        expr: up{job="spotify-mcp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Spotify MCP Server is down"
          description: "Service has been down for 1 minute"
```

#### Alert Notifications
```python
# src/spotify_mcp/infrastructure/alerts/notifications.py
import aiohttp
from typing import Dict, Any

class AlertNotifier:
    """Send alert notifications to various channels"""

    async def notify_slack(self, webhook_url: str, alert: Dict[str, Any]):
        """Send alert to Slack"""
        payload = {
            "text": f":rotating_light: Alert: {alert['summary']}",
            "attachments": [{
                "color": self._get_color(alert['severity']),
                "fields": [
                    {"title": "Severity", "value": alert['severity'], "short": True},
                    {"title": "Description", "value": alert['description'], "short": False}
                ]
            }]
        }

        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=payload)

    async def notify_email(self, smtp_config: Dict, alert: Dict[str, Any]):
        """Send alert via email"""
        # Implementation using aiosmtplib
        pass

    async def notify_pagerduty(self, api_key: str, alert: Dict[str, Any]):
        """Create PagerDuty incident"""
        # Implementation using PagerDuty Events API
        pass

    def _get_color(self, severity: str) -> str:
        colors = {
            'critical': 'danger',
            'warning': 'warning',
            'info': 'good'
        }
        return colors.get(severity, 'good')
```

---

## 🛡️ PHASE 4: Resilience & Reliability (Weeks 13-16)

**Goal:** 99.9% uptime with graceful failure handling
**Dependencies:** Phase 3 (metrics for circuit breaker)
**Deliverables:** Bulletproof error handling

### 4.1 Circuit Breaker Pattern (Week 13)

#### Implementation
```python
# src/spotify_mcp/infrastructure/resilience/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external API calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

        # Metrics
        self._state_changes = Counter(
            'circuit_breaker_state_changes_total',
            'Circuit breaker state changes',
            ['from_state', 'to_state']
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Service unavailable."
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.CLOSED)

        self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        logger.warning(
            f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}"
        )

        if self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if self.last_failure_time is None:
            return True

        return (
            datetime.utcnow() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        )

    def _transition_to(self, new_state: CircuitState):
        """Change circuit state"""
        old_state = self.state
        self.state = new_state

        self._state_changes.labels(
            from_state=old_state.value,
            to_state=new_state.value
        ).inc()

        logger.info(f"Circuit breaker: {old_state.value} -> {new_state.value}")

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Global circuit breaker for Spotify API
spotify_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=SpotifyAPIException
)

# Usage
async def get_track_with_circuit_breaker(client, track_id: str):
    return await spotify_circuit_breaker.call(
        client.track,
        track_id
    )
```

### 4.2 Advanced Retry Logic (Week 13)

#### Exponential Backoff with Jitter
```python
# src/spotify_mcp/infrastructure/resilience/retry.py
import asyncio
import random
from typing import Callable, Type, Tuple
from functools import wraps

class RetryStrategy:
    """Configurable retry strategy"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retriable_exceptions = retriable_exceptions

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        # Exponential backoff
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if should retry"""
        if attempt >= self.max_attempts:
            return False

        return isinstance(exception, self.retriable_exceptions)

def retry(strategy: RetryStrategy = None):
    """Decorator for retrying functions"""

    if strategy is None:
        strategy = RetryStrategy()

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(strategy.max_attempts):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if not strategy.should_retry(e, attempt):
                        raise

                    if attempt < strategy.max_attempts - 1:
                        delay = strategy.calculate_delay(attempt)
                        logger.info(
                            f"Retry attempt {attempt + 1}/{strategy.max_attempts} "
                            f"after {delay:.2f}s delay"
                        )
                        await asyncio.sleep(delay)

            # All retries exhausted
            raise last_exception

        return wrapper
    return decorator

# Predefined strategies
SPOTIFY_API_RETRY = RetryStrategy(
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0,
    jitter=True,
    retriable_exceptions=(SpotifyAPIException, RateLimitException)
)

NETWORK_RETRY = RetryStrategy(
    max_attempts=5,
    base_delay=2.0,
    max_delay=30.0,
    jitter=True,
    retriable_exceptions=(TimeoutError, ConnectionError)
)

# Usage
@retry(SPOTIFY_API_RETRY)
async def get_track_with_retry(client, track_id: str):
    return client.track(track_id)
```

### 4.3 Rate Limiting (Week 14)

#### Token Bucket Implementation
```python
# src/spotify_mcp/infrastructure/resilience/rate_limiter.py
import asyncio
from datetime import datetime
import time

class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(
        self,
        capacity: int,
        refill_rate: float,  # tokens per second
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens, wait if necessary"""
        async with self._lock:
            # Refill tokens based on time passed
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            # Calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate

            await asyncio.sleep(wait_time)

            # Try again after waiting
            self.tokens = tokens
            return True

    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire without waiting"""
        async with self._lock:
            # Refill tokens
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

class RateLimiter:
    """Multi-tier rate limiter"""

    def __init__(self):
        # Spotify API limits (example values, adjust based on actual limits)
        self.per_second = TokenBucket(capacity=10, refill_rate=10)
        self.per_minute = TokenBucket(capacity=100, refill_rate=100/60)
        self.per_hour = TokenBucket(capacity=1000, refill_rate=1000/3600)

    async def acquire(self):
        """Acquire permission for one request"""
        await self.per_second.acquire()
        await self.per_minute.acquire()
        await self.per_hour.acquire()

    async def try_acquire(self) -> bool:
        """Try to acquire without waiting"""
        return (
            await self.per_second.try_acquire() and
            await self.per_minute.try_acquire() and
            await self.per_hour.try_acquire()
        )

# Global rate limiter
rate_limiter = RateLimiter()

# Decorator
def rate_limited(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await rate_limiter.acquire()
        return await func(*args, **kwargs)
    return wrapper

# Usage
@rate_limited
async def spotify_api_call(client, method: str, *args, **kwargs):
    return await getattr(client, method)(*args, **kwargs)
```

### 4.4 Bulkhead Pattern (Week 14)

#### Resource Isolation
```python
# src/spotify_mcp/infrastructure/resilience/bulkhead.py
import asyncio
from typing import Callable, Any

class Bulkhead:
    """Isolate resources to prevent cascade failures"""

    def __init__(
        self,
        max_concurrent: int,
        max_queued: int = 0
    ):
        self.max_concurrent = max_concurrent
        self.max_queued = max_queued
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue_size = 0
        self._lock = asyncio.Lock()

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function within bulkhead limits"""

        # Check queue limit
        async with self._lock:
            if self.queue_size >= self.max_queued:
                raise BulkheadFullError(
                    f"Bulkhead queue is full ({self.max_queued})"
                )
            self.queue_size += 1

        try:
            async with self.semaphore:
                async with self._lock:
                    self.queue_size -= 1

                return await func(*args, **kwargs)

        except Exception:
            async with self._lock:
                self.queue_size -= 1
            raise

class BulkheadFullError(Exception):
    """Raised when bulkhead is at capacity"""
    pass

# Create separate bulkheads for different operation types
playback_bulkhead = Bulkhead(max_concurrent=5, max_queued=10)
search_bulkhead = Bulkhead(max_concurrent=10, max_queued=20)
library_bulkhead = Bulkhead(max_concurrent=3, max_queued=5)

# Usage
async def play_with_bulkhead(client, uri: str):
    return await playback_bulkhead.execute(
        client.start_playback,
        uris=[uri]
    )
```

### 4.5 Graceful Degradation (Week 15-16)

#### Fallback Mechanisms
```python
# src/spotify_mcp/infrastructure/resilience/fallback.py
from typing import Callable, Any, Optional
from functools import wraps

class FallbackChain:
    """Chain of fallback strategies"""

    def __init__(self):
        self.fallbacks = []

    def add(self, func: Callable, condition: Callable[[Exception], bool] = None):
        """Add fallback function"""
        self.fallbacks.append((func, condition))
        return self

    async def execute(self, primary: Callable, *args, **kwargs) -> Any:
        """Execute with fallback chain"""

        # Try primary function
        try:
            return await primary(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary function failed: {e}")

            # Try fallbacks in order
            for fallback_func, condition in self.fallbacks:
                if condition is None or condition(e):
                    try:
                        logger.info(f"Trying fallback: {fallback_func.__name__}")
                        return await fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.warning(f"Fallback failed: {fallback_error}")
                        continue

            # All fallbacks exhausted
            raise

# Example: Get track with fallbacks
async def get_track_from_api(client, track_id: str):
    """Primary: Get from Spotify API"""
    return client.track(track_id)

async def get_track_from_cache(client, track_id: str):
    """Fallback 1: Get from cache (even if expired)"""
    cache_key = f"track:{track_id}"
    cached = await cache.get(cache_key, ignore_expiry=True)
    if cached:
        logger.info("Returning stale cached data")
        return cached
    raise CacheError("No cached data available")

async def get_track_minimal(client, track_id: str):
    """Fallback 2: Return minimal data"""
    return {
        'id': track_id,
        'uri': f'spotify:track:{track_id}',
        'name': 'Unknown Track',
        '_degraded': True
    }

# Setup fallback chain
track_fallback = FallbackChain()
track_fallback.add(get_track_from_cache, lambda e: isinstance(e, SpotifyAPIException))
track_fallback.add(get_track_minimal, lambda e: True)  # Always as last resort

async def get_track(client, track_id: str):
    return await track_fallback.execute(
        get_track_from_api,
        client,
        track_id
    )
```

#### Health Checks
```python
# src/spotify_mcp/infrastructure/health/checks.py
from datetime import datetime
from typing import Dict, Any
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """Health check system"""

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            'spotify_api': await self._check_spotify_api(),
            'cache': await self._check_cache(),
            'database': await self._check_database(),
        }

        # Determine overall status
        statuses = [check['status'] for check in checks.values()]

        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        else:
            overall = HealthStatus.DEGRADED

        return {
            'status': overall.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {k: v for k, v in checks.items()}
        }

    async def _check_spotify_api(self) -> Dict:
        """Check Spotify API connectivity"""
        try:
            # Try a simple API call
            result = await spotify_client.current_user()
            return {
                'status': HealthStatus.HEALTHY,
                'latency_ms': result.get('_latency'),
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e)
            }

    async def _check_cache(self) -> Dict:
        """Check cache health"""
        try:
            stats = await cache.get_stats()

            hit_rate = float(stats['hit_rate'].rstrip('%'))
            status = (
                HealthStatus.HEALTHY if hit_rate > 50
                else HealthStatus.DEGRADED
            )

            return {
                'status': status,
                'hit_rate': stats['hit_rate'],
                'size': stats['size']
            }
        except Exception as e:
            return {
                'status': HealthStatus.DEGRADED,
                'error': str(e)
            }

    async def _check_database(self) -> Dict:
        """Check database connectivity"""
        try:
            # Simple query
            await db.execute("SELECT 1")
            return {'status': HealthStatus.HEALTHY}
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e)
            }
```

---

**Continue in next part - This is getting very long. Should I continue with the remaining phases (5-15)?**

Let me know if you want me to:
1. ✅ Continue with ALL remaining phases in the same detail
2. ✅ Create separate files for each phase
3. ✅ Start implementing Phase 1 immediately

What's your preference?

# Database Requirements Assessment

**Date**: November 18, 2025
**Project**: Spotify MCP Server v1.1.0
**Status**: Phase 1 Week 4

---

## Executive Summary

After thorough analysis of the Spotify MCP Server architecture and use cases, **a database is NOT currently required** for the core functionality. The server operates as a stateless proxy to Spotify's Web API, with caching handled by Redis/memory.

However, future features requiring persistent user data or analytics would benefit from database integration.

## Current Architecture Analysis

### Stateless Design

The Spotify MCP Server is designed as a stateless API proxy:

```
User/AI → MCP Server → Spotify Web API
                ↓
            Redis Cache (ephemeral)
```

**Key Characteristics:**
- No persistent state required
- Spotify API is source of truth
- Session data handled by spotipy (OAuth tokens in cache dir)
- Cache layer handles performance (Redis/memory)

### Data Flow

1. **Request Received**: User makes request via MCP protocol
2. **Cache Check**: Check Redis/memory cache
3. **API Call**: If cache miss, call Spotify API
4. **Response**: Return data to user
5. **Cache Store**: Store in cache with TTL

**No persistent storage needed** in this flow.

## Current Data Storage

### What We Store Today

| Data Type | Storage | Persistence | Purpose |
|-----------|---------|-------------|---------|
| OAuth tokens | File system (.cache-*) | Yes (managed by spotipy) | Authentication |
| Cache data | Redis/Memory | No (TTL-based) | Performance |
| Metrics | Prometheus | No (time-series, external) | Monitoring |
| Logs | File/stdout | Optional | Debugging |
| Config | Environment vars | No | Configuration |

**None of these require a traditional database.**

## Scenarios NOT Requiring a Database

### 1. Stateless API Proxy (Current)
✅ **No database needed**

The server proxies requests to Spotify's API. Spotify maintains all persistent data (playlists, saved tracks, user preferences).

### 2. Caching
✅ **No database needed**

Redis or memory cache handles performance. Data is ephemeral with TTL.
- Cache entries expire automatically
- No historical data analysis needed
- Source of truth is Spotify API

### 3. Configuration
✅ **No database needed**

Environment variables and `.env` files handle configuration.
- Loaded at startup
- Type-safe with Pydantic
- Environment-specific configs

### 4. Metrics
✅ **No database needed**

Prometheus time-series database handles metrics.
- Purpose-built for metrics
- Grafana for visualization
- Not appropriate for relational database

## Scenarios That WOULD Benefit from a Database

### 1. Multi-User Support ⚠️

**Use Case**: Support multiple Spotify accounts with different configurations

**Requirements**:
- Store user profiles
- Map user IDs to OAuth tokens
- User-specific preferences
- Access control

**Schema**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    spotify_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB
);

CREATE TABLE auth_tokens (
    user_id UUID REFERENCES users(id),
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Complexity**: Medium
**Value**: High (for multi-tenant deployments)

### 2. Listening History Analysis 📊

**Use Case**: Analyze listening patterns, generate insights

**Requirements**:
- Store play history
- Track favorite artists/genres
- Generate personalized reports
- Long-term trend analysis

**Schema**:
```sql
CREATE TABLE listening_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    track_id VARCHAR(255) NOT NULL,
    track_name TEXT,
    artist_name TEXT,
    played_at TIMESTAMP NOT NULL,
    duration_ms INTEGER,
    skipped BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_listening_history_user ON listening_history(user_id, played_at);
CREATE INDEX idx_listening_history_track ON listening_history(track_id);
```

**Complexity**: High
**Value**: Medium (Spotify already provides this via API)

### 3. Custom Recommendations 🎯

**Use Case**: Build ML models for personalized recommendations

**Requirements**:
- Store user interaction data
- Track likes/dislikes
- Store recommendation feedback
- Train custom models

**Schema**:
```sql
CREATE TABLE track_ratings (
    user_id UUID REFERENCES users(id),
    track_id VARCHAR(255) NOT NULL,
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, track_id)
);

CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    track_id VARCHAR(255) NOT NULL,
    feedback VARCHAR(20) CHECK (feedback IN ('like', 'dislike', 'skip')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Complexity**: Very High
**Value**: Medium (requires ML infrastructure)

### 4. Queue Management & Playlists 📝

**Use Case**: Persistent queues and collaborative playlists

**Requirements**:
- Store custom queues
- Collaborative playlist editing
- Playlist version history
- Offline queue management

**Schema**:
```sql
CREATE TABLE custom_queues (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE queue_items (
    id SERIAL PRIMARY KEY,
    queue_id UUID REFERENCES custom_queues(id) ON DELETE CASCADE,
    track_id VARCHAR(255) NOT NULL,
    position INTEGER NOT NULL,
    added_by UUID REFERENCES users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(queue_id, position)
);
```

**Complexity**: Medium
**Value**: Low (Spotify API handles this)

## Recommended Approach

### Phase 1: No Database (CURRENT) ✅

**Recommended for:**
- Single-user deployments
- Stateless API proxy use case
- MCP protocol integration
- AI assistant integration

**Rationale:**
- Keeps architecture simple
- No database maintenance overhead
- Spotify API is source of truth
- Faster development/deployment

### Phase 2: Database (FUTURE) 🔮

**Recommended when:**
- Multi-user support needed
- Custom analytics required
- Building SaaS product
- Compliance/audit trail needed

**Technology Recommendations:**

#### For Multi-User Support
- **PostgreSQL** - Mature, reliable, excellent JSON support
- **Migration Tool** - Alembic (already planned)
- **ORM** - SQLAlchemy 2.0 (async support)

#### For Analytics
- **PostgreSQL** - Good for structured queries
- **ClickHouse** - Better for analytical workloads
- **TimescaleDB** - PostgreSQL extension for time-series

#### For Simple Key-Value
- **Redis** - Already using for cache, can extend
- **SQLite** - Simple, serverless, good for single-user

## Minimal Database Implementation (If Needed)

If database becomes necessary, here's a minimal implementation:

### 1. Database Setup

```bash
# Install dependencies
pip install sqlalchemy alembic psycopg2-binary

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "initial schema"

# Run migration
alembic upgrade head
```

### 2. Minimal Schema

```python
# src/spotify_mcp/database/models.py
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_user_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255))
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 3. Database Configuration

```python
# Add to config/settings.py
class DatabaseConfig(BaseModel):
    url: str = Field(
        default="postgresql://user:pass@localhost/spotify_mcp",
        description="Database connection URL"
    )
    pool_size: int = Field(default=5, gt=0)
    echo: bool = Field(default=False)

    @classmethod
    def from_env(cls):
        return cls(
            url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/spotify_mcp"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
```

### 4. Session Management

```python
# src/spotify_mcp/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

engine = None
async_session_factory = None

def init_database(database_url: str):
    global engine, async_session_factory

    engine = create_async_engine(database_url, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

@asynccontextmanager
async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Cost-Benefit Analysis

### Without Database

**Costs:**
- ❌ Limited to single-user scenarios
- ❌ No historical data analysis
- ❌ No custom recommendations

**Benefits:**
- ✅ Simple architecture
- ✅ Lower operational cost
- ✅ Faster deployment
- ✅ No database maintenance
- ✅ Stateless and scalable

### With Database

**Costs:**
- ❌ Increased complexity
- ❌ Database maintenance overhead
- ❌ Higher infrastructure cost
- ❌ Need for migrations/backups
- ❌ Potential performance bottleneck

**Benefits:**
- ✅ Multi-user support
- ✅ Historical data analysis
- ✅ Custom features (recommendations, analytics)
- ✅ Audit trail
- ✅ Offline capabilities

## Conclusion

### Recommendation: NO DATABASE FOR v1.x

**Rationale:**
1. **Current Use Case**: Stateless API proxy doesn't need persistent storage
2. **Spotify API**: Already handles all persistent data (playlists, saved tracks, user prefs)
3. **Caching**: Redis handles performance without database complexity
4. **Simplicity**: Keeping architecture simple enables faster iteration
5. **Scalability**: Stateless design scales horizontally without database bottleneck

### Future Consideration: Database for v2.x (If Needed)

If the product evolves to include:
- **Multi-tenant SaaS** - Database required for user management
- **Analytics Dashboard** - Database useful for historical analysis
- **Custom Recommendations** - Database needed for ML features
- **Compliance Requirements** - Database required for audit trails

Then revisit with PostgreSQL + Alembic migration tool.

---

## Action Items

- [x] Assess database requirements
- [x] Document current architecture
- [x] Evaluate future scenarios
- [x] Recommend approach
- [ ] **Decision**: Proceed WITHOUT database for v1.x
- [ ] If needs change: Implement minimal schema from this document

---

**Status**: ✅ Assessment Complete - No database required for current scope

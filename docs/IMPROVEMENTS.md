# Spotify MCP Server - Final Improvement Roadmap

> **Version:** 2.0.0 → 3.0.0 Migration Plan  
> **MCP SDK:** v1.23.1  
> **Protocol:** 2025-06-18  
> **Status:** Completed – FastMCP v3.0 live  
> **Created:** Based on comprehensive MCP SDK & Protocol analysis

---

## Executive Summary

This document outlines the comprehensive improvement plan for migrating the Spotify MCP Server from the current low-level `Server` class architecture to the modern **FastMCP** pattern. The migration will bring full compliance with MCP SDK v1.23.1 best practices, improved maintainability, and enhanced feature support.

### Current State
- **81 tools** (fully migrated, annotated) ✅
- **10 resources** (4 static + 6 templates) ✅
- **Prompts:** Not needed for current scope
- **Architecture:** FastMCP decorator-based server (`spotify_server.py`)
- **Client Management:** Lifespan-managed `AppContext`
- **Context:** Full Context injection with progress/logging
- **Lifecycle:** Async lifespan with proper startup/shutdown

### Target State (achieved)
- **81 tools** with annotations and structured output
- **10 resources** with dynamic templates
- **Architecture:** FastMCP with decorator-based registration
- **Client Management:** Lifespan-managed initialization
- **Context:** Full Context injection across all tools
- **Lifecycle:** Typed startup/shutdown lifecycle

---

## Table of Contents

1. [Critical Priority Improvements](#1-critical-priority-improvements)
2. [High Priority Improvements](#2-high-priority-improvements)
3. [Medium Priority Improvements](#3-medium-priority-improvements)
4. [Low Priority Improvements](#4-low-priority-improvements)
5. [Future Considerations](#5-future-considerations)
6. [Migration Roadmap](#6-migration-roadmap)
7. [Breaking Changes](#7-breaking-changes)
8. [Testing Strategy](#8-testing-strategy)

---

## 1. Critical Priority Improvements

### 1.1 Migrate to FastMCP Class

**Current Implementation:**
```python
from mcp.server import Server
server = Server("spotify-mcp")

TOOL_FUNCTIONS = {
    "get_current_playback": get_current_playback,
    "play_music": play_music,
    # ... 73 more entries
}
```

**Target Implementation:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="spotify-mcp",
    version="3.0.0",
    capabilities=ServerCapabilities(
        tools=ToolsCapability(listChanged=True),
        resources=ResourcesCapability(subscribe=True, listChanged=True),
        prompts=PromptsCapability(listChanged=True),
        logging=LoggingCapability()
    )
)
```

**Why Critical:**
- FastMCP is the **recommended** approach in MCP SDK v1.23.1
- Reduces boilerplate by 60-70%
- Enables all modern features (Context, lifespan, decorators)
- Better type safety and IDE support

**Impact:**
- `src/spotify_mcp/server.py` - Complete rewrite
- All tool handlers - Minor signature changes
- Tests - Update imports and mocking

---

### 1.2 Implement Lifespan Management

**Current Problem:**
```python
# Global client pattern - anti-pattern
_spotify_client: SpotifyClient | None = None

async def get_spotify_client():
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient()
    return _spotify_client
```

**Target Implementation:**
```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class AppContext:
    spotify_client: SpotifyClient
    rate_limiter: RateLimiter
    cache: CacheManager

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage Spotify client lifecycle with proper startup/shutdown."""
    # Startup
    spotify_client = SpotifyClient()
    await spotify_client.initialize()
    
    rate_limiter = RateLimiter(calls_per_minute=100)
    cache = CacheManager(ttl=300)
    
    try:
        yield AppContext(
            spotify_client=spotify_client,
            rate_limiter=rate_limiter,
            cache=cache
        )
    finally:
        # Shutdown - proper cleanup
        await spotify_client.close()
        await cache.flush()

mcp = FastMCP("spotify-mcp", lifespan=app_lifespan)
```

**Why Critical:**
- Proper resource cleanup prevents connection leaks
- Typed context provides dependency injection
- Centralized initialization point
- Graceful shutdown handling

**Benefits:**
- No more global state
- Testable with dependency injection
- Proper async cleanup
- Type-safe context access in all tools

---

### 1.3 Add Context Injection to All Tools

**Current Implementation:**
```python
async def get_current_playback() -> list[types.TextContent]:
    client = await get_spotify_client()
    # No access to logging, progress, or session info
    result = await client.get_playback_state()
    return [types.TextContent(type="text", text=json.dumps(result))]
```

**Target Implementation:**
```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def get_current_playback(ctx: Context[AppContext]) -> list[types.TextContent]:
    """Get current playback state from Spotify."""
    # Access typed lifespan context
    client = ctx.request_context.lifespan_context.spotify_client
    
    # Structured logging
    await ctx.info("Fetching current playback state")
    
    # Progress reporting for long operations
    await ctx.report_progress(0, 100, "Connecting to Spotify...")
    
    result = await client.get_playback_state()
    
    await ctx.report_progress(100, 100, "Playback state retrieved")
    
    return [types.TextContent(type="text", text=json.dumps(result))]
```

**Context Capabilities:**
| Method | Purpose |
|--------|---------|
| `ctx.info(message)` | Log informational messages |
| `ctx.debug(message)` | Log debug messages |
| `ctx.warning(message)` | Log warnings |
| `ctx.error(message)` | Log errors |
| `ctx.report_progress(current, total, message)` | Progress notifications |
| `ctx.request_context.session` | Access session information |
| `ctx.request_context.lifespan_context` | Access typed app context |

**Why Critical:**
- Enables progress reporting for long operations (playlist creation, bulk operations)
- Structured logging for debugging
- Access to session/request metadata
- Required for enterprise monitoring

---

## 2. High Priority Improvements

### 2.1 Convert to Decorator-Based Tool Registration

**Current Pattern:**
```python
# Manual dictionary - error-prone, no type checking
TOOL_FUNCTIONS = {
    "get_current_playback": get_current_playback,
    "play_music": play_music,
    "pause_music": pause_music,
    # 72 more entries...
}

@server.list_tools()
async def list_tools():
    return [
        types.Tool(name="get_current_playback", ...),
        types.Tool(name="play_music", ...),
        # Manual sync required with TOOL_FUNCTIONS
    ]
```

**Target Pattern:**
```python
@mcp.tool(
    description="Get current playback state including track, progress, and device",
    annotations=ToolAnnotations(
        title="Get Playback",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False
    )
)
async def get_current_playback(ctx: Context[AppContext]) -> dict:
    """Decorator handles registration automatically."""
    ...

@mcp.tool(
    description="Start or resume playback",
    annotations=ToolAnnotations(
        title="Play Music",
        readOnlyHint=False,  # Modifies state
        idempotentHint=False,  # Not idempotent
        destructiveHint=False
    )
)
async def play_music(
    ctx: Context[AppContext],
    uri: str = None,
    device_id: str = None
) -> dict:
    ...
```

**Benefits:**
- Automatic tool registration
- Type inference for parameters
- Co-located tool definition and implementation
- Eliminates sync bugs between TOOL_FUNCTIONS and list_tools

---

### 2.2 Add Tool Annotations

**MCP Protocol Tool Annotations:**

| Annotation | Type | Purpose |
|------------|------|---------|
| `title` | string | Human-readable display name |
| `readOnlyHint` | boolean | Tool only reads data (GET operations) |
| `idempotentHint` | boolean | Safe to retry (same result each time) |
| `destructiveHint` | boolean | Makes irreversible changes |
| `openWorldHint` | boolean | Interacts with external entities |

**Tool Classification for Spotify MCP:**

```python
# Read-only tools (23 tools)
READ_ONLY_TOOLS = [
    "get_current_playback",
    "get_queue",
    "get_devices",
    "get_user_profile",
    "get_playlists",
    "search_spotify",
    # ... etc
]

# Idempotent tools (15 tools)
IDEMPOTENT_TOOLS = [
    "pause_music",      # Pausing twice = same state
    "set_volume",       # Setting volume 50 twice = 50
    "set_repeat_mode",  # Setting repeat twice = same mode
    # ... etc
]

# Destructive tools (5 tools)
DESTRUCTIVE_TOOLS = [
    "delete_playlist",
    "unfollow_playlist",
    "remove_from_library",
    # ... etc
]
```

**Implementation Example:**
```python
@mcp.tool(annotations=ToolAnnotations(
    title="Delete Playlist",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=True,  # Irreversible!
    openWorldHint=False
))
async def delete_playlist(ctx: Context, playlist_id: str) -> dict:
    """Permanently delete a playlist. This action cannot be undone."""
    ...
```

**Why Important:**
- Helps Claude understand tool behavior
- Enables smarter tool selection
- Provides safety hints for destructive operations
- Improves user trust and transparency

---

### 2.3 Implement Resource Templates

**Current Static Resources:**
```python
RESOURCES = [
    Resource(uri="spotify://playback/current", ...),
    Resource(uri="spotify://user/profile", ...),
    Resource(uri="spotify://user/top-tracks", ...),
    # Static URIs only
]
```

**Target Dynamic Templates:**
```python
@mcp.resource("spotify://track/{track_id}")
async def get_track_resource(ctx: Context, track_id: str) -> Resource:
    """Dynamic resource for any track by ID."""
    client = ctx.request_context.lifespan_context.spotify_client
    track = await client.get_track(track_id)
    return Resource(
        uri=f"spotify://track/{track_id}",
        name=track["name"],
        description=f"Track: {track['name']} by {track['artists'][0]['name']}",
        mimeType="application/json",
        annotations=ResourceAnnotations(
            audience=["user"],
            priority=0.8
        )
    )

@mcp.resource("spotify://playlist/{playlist_id}")
async def get_playlist_resource(ctx: Context, playlist_id: str) -> Resource:
    """Dynamic resource for any playlist."""
    ...

@mcp.resource("spotify://artist/{artist_id}")
async def get_artist_resource(ctx: Context, artist_id: str) -> Resource:
    """Dynamic resource for any artist."""
    ...

@mcp.resource("spotify://album/{album_id}")
async def get_album_resource(ctx: Context, album_id: str) -> Resource:
    """Dynamic resource for any album."""
    ...
```

**Proposed Resource Template Structure:**

| Template | Description |
|----------|-------------|
| `spotify://track/{track_id}` | Individual track details |
| `spotify://album/{album_id}` | Album with tracks |
| `spotify://artist/{artist_id}` | Artist info and top tracks |
| `spotify://playlist/{playlist_id}` | Playlist with tracks |
| `spotify://episode/{episode_id}` | Podcast episode |
| `spotify://show/{show_id}` | Podcast show |
| `spotify://user/{user_id}` | User profile |

**Benefits:**
- Dynamic content fetching
- Cleaner URI scheme (Spotify-native patterns)
- Supports autocomplete for URIs
- Enables resource subscriptions

---

### 2.4 Add Structured Output (outputSchema)

**Current Approach:**
```python
# Unstructured JSON string output
return [types.TextContent(
    type="text",
    text=json.dumps({"track": "...", "artist": "..."})
)]
```

**Target Approach:**
```python
from pydantic import BaseModel

class PlaybackState(BaseModel):
    is_playing: bool
    track_name: str
    artist_name: str
    album_name: str
    progress_ms: int
    duration_ms: int
    device_name: str
    shuffle_state: bool
    repeat_state: str

@mcp.tool(output_schema=PlaybackState)
async def get_current_playback(ctx: Context) -> PlaybackState:
    """Returns typed, validated playback state."""
    client = ctx.request_context.lifespan_context.spotify_client
    state = await client.get_playback_state()
    
    return PlaybackState(
        is_playing=state["is_playing"],
        track_name=state["item"]["name"],
        artist_name=state["item"]["artists"][0]["name"],
        # ... etc
    )
```

**Key Output Models to Define:**

| Model | Tools Using It |
|-------|----------------|
| `PlaybackState` | get_current_playback |
| `Track` | search_tracks, get_track |
| `Playlist` | get_playlist, create_playlist |
| `Artist` | search_artists, get_artist |
| `Album` | search_albums, get_album |
| `Device` | get_devices |
| `Queue` | get_queue |
| `UserProfile` | get_user_profile |

**Benefits:**
- Type validation at runtime
- Self-documenting API
- Better Claude understanding of response structure
- IDE autocomplete for tool outputs

---

## 3. Medium Priority Improvements

### 3.1 Implement Progress Notifications

**Use Cases for Progress Reporting:**

| Operation | Why Progress Needed |
|-----------|---------------------|
| `create_playlist_from_recommendations` | Multiple API calls |
| `add_tracks_to_playlist` (bulk) | Many tracks to add |
| `get_all_playlist_tracks` | Paginated fetching |
| `search_and_play` | Search + playback |
| `discover_weekly_analysis` | Analysis of 30+ tracks |

**Implementation:**
```python
@mcp.tool()
async def create_playlist_from_recommendations(
    ctx: Context[AppContext],
    seed_tracks: list[str],
    playlist_name: str,
    track_count: int = 20
) -> dict:
    """Create a playlist from recommendations with progress updates."""
    
    await ctx.report_progress(0, 100, "Analyzing seed tracks...")
    
    # Step 1: Get recommendations
    await ctx.report_progress(20, 100, "Fetching recommendations...")
    recommendations = await client.get_recommendations(seed_tracks)
    
    # Step 2: Create playlist
    await ctx.report_progress(50, 100, "Creating playlist...")
    playlist = await client.create_playlist(playlist_name)
    
    # Step 3: Add tracks
    await ctx.report_progress(70, 100, "Adding tracks to playlist...")
    await client.add_tracks_to_playlist(playlist["id"], recommendations)
    
    await ctx.report_progress(100, 100, "Playlist created successfully!")
    
    return {"playlist_id": playlist["id"], "tracks_added": len(recommendations)}
```

---

### 3.2 Implement Logging Capability

**MCP Logging Levels (RFC 5424):**

| Level | Severity | Use Case |
|-------|----------|----------|
| `debug` | Detailed debugging | API call details |
| `info` | General information | Operation progress |
| `notice` | Significant events | Config changes |
| `warning` | Warning conditions | Rate limit approaching |
| `error` | Error conditions | API failures |
| `critical` | Critical conditions | Auth failures |
| `alert` | Immediate action | Token expiration |
| `emergency` | System unusable | Server crash |

**Implementation:**
```python
@mcp.tool()
async def search_spotify(
    ctx: Context[AppContext],
    query: str,
    type: str = "track",
    limit: int = 20
) -> dict:
    await ctx.debug(f"Search request: query='{query}', type='{type}', limit={limit}")
    
    try:
        results = await client.search(query, type, limit)
        await ctx.info(f"Search returned {len(results['items'])} results")
        return results
    except RateLimitError as e:
        await ctx.warning(f"Rate limit approaching: {e.retry_after}s")
        raise
    except SpotifyAPIError as e:
        await ctx.error(f"Spotify API error: {e.message}")
        raise
```

---

### 3.3 Add Completion Handlers (Autocomplete)

**For Resource URIs:**
```python
@mcp.complete("spotify://playlist/{playlist_id}")
async def complete_playlist_id(ctx: Context, prefix: str) -> list[str]:
    """Provide autocomplete for playlist IDs."""
    client = ctx.request_context.lifespan_context.spotify_client
    playlists = await client.get_user_playlists(limit=50)
    
    completions = []
    for playlist in playlists["items"]:
        if prefix.lower() in playlist["name"].lower():
            completions.append(playlist["id"])
    
    return completions[:10]  # Limit suggestions
```

**For Prompt Arguments:**
```python
@mcp.complete("discover_new_music", "genre")
async def complete_genre(ctx: Context, prefix: str) -> list[str]:
    """Provide autocomplete for genre argument."""
    all_genres = [
        "pop", "rock", "hip-hop", "electronic", "jazz", "classical",
        "country", "r-n-b", "latin", "indie", "metal", "folk"
    ]
    return [g for g in all_genres if g.startswith(prefix.lower())]
```

---

### 3.4 Resource Subscriptions

**Enable Real-Time Updates:**
```python
# Server capability
mcp = FastMCP(
    "spotify-mcp",
    capabilities=ServerCapabilities(
        resources=ResourcesCapability(
            subscribe=True,  # Enable subscriptions
            listChanged=True
        )
    )
)

# Handle subscription requests
@mcp.on_subscribe("spotify://playback/current")
async def subscribe_playback(ctx: Context) -> None:
    """Start sending playback updates."""
    # Implementation would poll Spotify and send notifications
    pass

@mcp.on_unsubscribe("spotify://playback/current")
async def unsubscribe_playback(ctx: Context) -> None:
    """Stop sending playback updates."""
    pass
```

**Subscribable Resources:**

| Resource | Update Frequency | Use Case |
|----------|------------------|----------|
| `spotify://playback/current` | 1s polling | Now playing updates |
| `spotify://queue` | On change | Queue modifications |
| `spotify://user/recently-played` | 30s polling | Listening history |

---

## 4. Low Priority Improvements

### 4.1 Multi-Modal Prompt Support

**Current Prompt Structure:**
```python
@mcp.prompt()
async def discover_new_music(genre: str) -> list[PromptMessage]:
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Find new {genre} music..."
            )
        )
    ]
```

**Enhanced with Embedded Resources:**
```python
@mcp.prompt()
async def analyze_listening_history(ctx: Context) -> list[PromptMessage]:
    # Fetch data to embed
    client = ctx.request_context.lifespan_context.spotify_client
    recent = await client.get_recently_played(limit=20)
    top_tracks = await client.get_top_tracks(limit=10)
    
    return [
        PromptMessage(
            role="user",
            content=[
                TextContent(
                    type="text",
                    text="Analyze my listening patterns:"
                ),
                EmbeddedResource(
                    type="resource",
                    resource=Resource(
                        uri="spotify://user/recently-played",
                        text=json.dumps(recent)
                    )
                ),
                EmbeddedResource(
                    type="resource",
                    resource=Resource(
                        uri="spotify://user/top-tracks",
                        text=json.dumps(top_tracks)
                    )
                )
            ]
        )
    ]
```

---

### 4.2 Cancellation Support

**For Long-Running Operations:**
```python
@mcp.tool()
async def analyze_playlist(ctx: Context, playlist_id: str) -> dict:
    """Analyze a playlist with cancellation support."""
    tracks = await client.get_playlist_tracks(playlist_id)
    
    results = []
    for i, track in enumerate(tracks):
        # Check for cancellation
        if ctx.cancelled:
            await ctx.info("Analysis cancelled by user")
            return {"status": "cancelled", "processed": i}
        
        # Analyze track
        audio_features = await client.get_audio_features(track["id"])
        results.append(audio_features)
        
        await ctx.report_progress(i + 1, len(tracks), f"Analyzing track {i + 1}/{len(tracks)}")
    
    return {"tracks_analyzed": len(results), "features": results}
```

---

### 4.3 Enhanced Error Responses

**Structured Error Information:**
```python
class SpotifyMCPError(Exception):
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data or {}

# Error codes
class ErrorCodes:
    AUTHENTICATION_FAILED = -32001
    RATE_LIMITED = -32002
    RESOURCE_NOT_FOUND = -32003
    PLAYBACK_ERROR = -32004
    INVALID_URI = -32005

@mcp.tool()
async def play_track(ctx: Context, uri: str) -> dict:
    try:
        await client.play(uri)
        return {"status": "playing"}
    except SpotifyAuthError:
        raise SpotifyMCPError(
            code=ErrorCodes.AUTHENTICATION_FAILED,
            message="Spotify authentication required",
            data={"auth_url": get_auth_url()}
        )
    except SpotifyNotFoundError:
        raise SpotifyMCPError(
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message=f"Track not found: {uri}",
            data={"uri": uri}
        )
```

---

### 4.4 Testing with In-Memory Client

**MCP SDK Testing Utilities:**
```python
from mcp.shared.memory import create_connected_server_and_client_session

async def test_get_current_playback():
    """Test tool execution with in-memory transport."""
    async with create_connected_server_and_client_session(mcp._mcp_server) as (
        server_session,
        client_session
    ):
        # Call tool via client
        result = await client_session.call_tool(
            "get_current_playback",
            {}
        )
        
        assert result.content[0].type == "text"
        data = json.loads(result.content[0].text)
        assert "is_playing" in data
```

---

## 5. Future Considerations

### 5.1 Sampling Support (Agentic Behaviors)

**Potential Use Cases:**
- Automatic playlist curation based on mood analysis
- Smart recommendations with LLM-powered reasoning
- Conversational music discovery

**Note:** Requires client to declare `sampling` capability. Most current clients (Claude Desktop) may not support this yet.

### 5.2 Streamable HTTP Transport

**For Web Deployment:**
- Current: stdio transport only
- Future: Add Streamable HTTP for web-based MCP clients
- Security: Implement Origin validation, session management

### 5.3 Multi-User Sessions

**Enterprise Feature:**
- Session-specific Spotify authentication
- Per-user rate limiting
- Audit logging per session

---

## 6. Migration Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Create `FastMCP` server instance
- [ ] Implement `AppContext` dataclass
- [ ] Add lifespan management with proper startup/shutdown
- [ ] Migrate 5 core tools to decorator pattern (proof of concept)
- [ ] Add Context injection to migrated tools
- [ ] Verify backward compatibility

### Phase 2: Full Tool Migration (Week 3-4)
- [ ] Migrate all 75 tools to decorator pattern
- [ ] Add tool annotations to all tools
- [ ] Classify tools by behavior (read-only, idempotent, destructive)
- [ ] Add progress reporting to long-running operations
- [ ] Implement structured logging

### Phase 3: Resources & Prompts (Week 5)
- [ ] Convert static resources to templates
- [ ] Add 7 new resource templates (track, album, artist, playlist, episode, show, user)
- [ ] Enhance prompts with embedded resources
- [ ] Add completion handlers for URIs and arguments

### Phase 4: Advanced Features (Week 6)
- [ ] Define output schemas (Pydantic models)
- [ ] Add cancellation support
- [ ] Implement resource subscriptions (if client support exists)
- [ ] Enhanced error responses

### Phase 5: Testing & Documentation (Week 7-8)
- [ ] Update all unit tests for FastMCP
- [ ] Add in-memory transport tests
- [ ] Update documentation for v3.0.0
- [ ] Performance benchmarking
- [ ] Security audit

---

## 7. Breaking Changes

### API Changes
| Change | Impact | Migration |
|--------|--------|-----------|
| Context parameter added | Tool signatures change | Add `ctx: Context` first param |
| Output schema enforcement | Strict return types | Define Pydantic models |
| Resource URI changes | URI format updates | Use template patterns |

### Removed Features
- Global `_spotify_client` pattern (replaced by lifespan context)
- Manual `TOOL_FUNCTIONS` dictionary (replaced by decorators)
- `@server.list_tools()` handler (automatic with FastMCP)

### Compatibility
- MCP protocol version: 2025-06-18 (latest)
- Python version: 3.10+ (unchanged)
- MCP SDK version: 1.23.1+ (bump required)

---

## 8. Testing Strategy

### Unit Tests
```python
# Test individual tools with mocked Spotify client
async def test_get_current_playback_returns_state():
    mock_client = AsyncMock()
    mock_client.get_playback_state.return_value = {...}
    
    ctx = create_test_context(spotify_client=mock_client)
    result = await get_current_playback(ctx)
    
    assert result.is_playing == True
```

### Integration Tests
```python
# Test full MCP flow with in-memory transport
async def test_tool_call_via_mcp():
    async with create_connected_server_and_client_session(mcp) as (server, client):
        result = await client.call_tool("get_current_playback", {})
        assert result.isError == False
```

### End-to-End Tests
```python
# Test with real Spotify API (requires credentials)
@pytest.mark.e2e
async def test_real_playback():
    # Only run in CI with real credentials
    ...
```

---

## Appendix: Reference Links

- [MCP Python SDK Documentation](https://modelcontextprotocol.io/sdks/python)
- [MCP Specification (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18)
- [FastMCP Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)
- [Tool Annotations](https://modelcontextprotocol.io/docs/concepts/tools#tool-annotations)
- [Resource Templates](https://modelcontextprotocol.io/docs/concepts/resources#resource-templates)
- [Progress Notifications](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/progress)
- [Logging](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging)

---

> **Next Steps:** Review this document, prioritize improvements, and begin Phase 1 implementation when approved.

*Document created based on comprehensive analysis of MCP Python SDK v1.23.1 and Protocol 2025-06-18*

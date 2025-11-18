# 🚀 Implementation Roadmap - Part 2: Developer Experience & Intelligence

## 🎨 PHASE 5: Developer Experience - SDK & CLI (Weeks 17-22)

**Goal:** Make the platform accessible to all developers, not just MCP users
**Dependencies:** Phase 1-4 (stable core)
**Deliverables:** Python SDK, CLI tool, TypeScript SDK

### 5.1 Python SDK Design (Week 17-18)

#### SDK Architecture
```python
# spotify_mcp_sdk/client.py
from typing import Optional, List, Dict, Any
import httpx
from .models import Track, Playlist, Album, Artist, User
from .exceptions import SpotifyMCPError, AuthenticationError

class SpotifyMCP:
    """
    High-level Python SDK for Spotify MCP Server

    Example:
        >>> mcp = SpotifyMCP(api_key="your_key")
        >>> track = mcp.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
        >>> mcp.playback.play(track.uri)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=timeout)

        # Resource namespaces
        self.playback = PlaybackResource(self)
        self.tracks = TrackResource(self)
        self.playlists = PlaylistResource(self)
        self.albums = AlbumResource(self)
        self.artists = ArtistResource(self)
        self.search = SearchResource(self)
        self.library = LibraryResource(self)
        self.user = UserResource(self)

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request to MCP server"""
        headers = kwargs.pop('headers', {})
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        url = f"{self.base_url}{endpoint}"

        try:
            response = await self.client.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            raise SpotifyMCPError(f"API error: {e}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


# Resource classes
class PlaybackResource:
    """Playback control operations"""

    def __init__(self, client: SpotifyMCP):
        self._client = client

    async def play(
        self,
        uri: Optional[str] = None,
        uris: Optional[List[str]] = None,
        context_uri: Optional[str] = None
    ) -> None:
        """
        Start or resume playback

        Args:
            uri: Single track/episode URI to play
            uris: List of URIs to play
            context_uri: Album/playlist context

        Example:
            >>> await mcp.playback.play(uri="spotify:track:...")
        """
        data = {}
        if uri:
            data['uris'] = [uri]
        elif uris:
            data['uris'] = uris
        if context_uri:
            data['context_uri'] = context_uri

        await self._client._request('POST', '/playback/play', json=data)

    async def pause(self) -> None:
        """Pause playback"""
        await self._client._request('POST', '/playback/pause')

    async def skip_next(self) -> None:
        """Skip to next track"""
        await self._client._request('POST', '/playback/next')

    async def skip_previous(self) -> None:
        """Skip to previous track"""
        await self._client._request('POST', '/playback/previous')

    async def set_volume(self, volume: int) -> None:
        """
        Set playback volume

        Args:
            volume: Volume level (0-100)
        """
        await self._client._request(
            'POST',
            '/playback/volume',
            json={'volume_percent': volume}
        )

    async def get_state(self) -> Dict[str, Any]:
        """Get current playback state"""
        return await self._client._request('GET', '/playback/state')

    async def get_currently_playing(self) -> Optional[Track]:
        """Get currently playing track"""
        state = await self.get_state()
        if state and state.get('item'):
            return Track.from_dict(state['item'])
        return None


class TrackResource:
    """Track operations"""

    def __init__(self, client: SpotifyMCP):
        self._client = client

    async def get(self, track_id: str) -> Track:
        """
        Get track by ID

        Args:
            track_id: Spotify track ID

        Returns:
            Track object

        Example:
            >>> track = await mcp.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
            >>> print(track.name)
        """
        data = await self._client._request('GET', f'/tracks/{track_id}')
        return Track.from_dict(data)

    async def get_many(self, track_ids: List[str]) -> List[Track]:
        """Get multiple tracks"""
        data = await self._client._request(
            'GET',
            '/tracks',
            params={'ids': ','.join(track_ids)}
        )
        return [Track.from_dict(t) for t in data['tracks']]

    async def get_audio_features(self, track_id: str) -> Dict[str, Any]:
        """Get audio features for track"""
        return await self._client._request(
            'GET',
            f'/tracks/{track_id}/audio-features'
        )


class SearchResource:
    """Search operations"""

    def __init__(self, client: SpotifyMCP):
        self._client = client

    async def search(
        self,
        query: str,
        types: List[str] = ['track'],
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for tracks, albums, artists, or playlists

        Args:
            query: Search query
            types: Resource types to search for
            limit: Number of results per type

        Returns:
            Dict with results by type

        Example:
            >>> results = await mcp.search.search("Beatles", types=['track', 'artist'])
            >>> for track in results['tracks']:
            ...     print(track.name)
        """
        return await self._client._request(
            'GET',
            '/search',
            params={
                'q': query,
                'type': ','.join(types),
                'limit': limit
            }
        )

    async def tracks(self, query: str, limit: int = 20) -> List[Track]:
        """Search for tracks only"""
        results = await self.search(query, types=['track'], limit=limit)
        return [Track.from_dict(t) for t in results.get('tracks', {}).get('items', [])]


# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Track(BaseModel):
    """Track model"""
    id: str
    name: str
    uri: str
    artists: List['Artist']
    album: 'Album'
    duration_ms: int
    explicit: bool
    popularity: int
    preview_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Track':
        """Create Track from API response"""
        return cls(**data)

    @property
    def duration_seconds(self) -> int:
        """Duration in seconds"""
        return self.duration_ms // 1000

    @property
    def artist_names(self) -> str:
        """Comma-separated artist names"""
        return ', '.join(a.name for a in self.artists)


class Playlist(BaseModel):
    """Playlist model"""
    id: str
    name: str
    uri: str
    description: Optional[str]
    owner: 'User'
    public: bool
    collaborative: bool
    tracks_total: int = Field(alias='tracks.total')

    async def get_tracks(self, mcp: SpotifyMCP) -> List[Track]:
        """Get all tracks in playlist"""
        return await mcp.playlists.get_tracks(self.id)

    async def add_tracks(self, mcp: SpotifyMCP, track_uris: List[str]):
        """Add tracks to playlist"""
        await mcp.playlists.add_tracks(self.id, track_uris)
```

#### Sync vs Async Support
```python
# spotify_mcp_sdk/sync_client.py
import asyncio
from typing import Optional
from .client import SpotifyMCP as AsyncSpotifyMCP

class SpotifyMCP:
    """
    Synchronous wrapper around async client

    Example:
        >>> mcp = SpotifyMCP(api_key="your_key")
        >>> track = mcp.tracks.get("3n3Ppam7vgaVa1iaRUc9Lp")
        >>> mcp.playback.play(track.uri)
    """

    def __init__(self, *args, **kwargs):
        self._async_client = AsyncSpotifyMCP(*args, **kwargs)
        self._loop = asyncio.new_event_loop()

        # Create sync wrappers for all resources
        self.playback = self._wrap_resource(self._async_client.playback)
        self.tracks = self._wrap_resource(self._async_client.tracks)
        # ... etc

    def _wrap_resource(self, async_resource):
        """Wrap async resource methods to be synchronous"""
        class SyncWrapper:
            def __init__(self, async_res, loop):
                self._async = async_res
                self._loop = loop

            def __getattr__(self, name):
                async_method = getattr(self._async, name)
                if asyncio.iscoroutinefunction(async_method):
                    return lambda *args, **kwargs: self._loop.run_until_complete(
                        async_method(*args, **kwargs)
                    )
                return async_method

        return SyncWrapper(async_resource, self._loop)

    def close(self):
        """Close client and event loop"""
        self._loop.run_until_complete(self._async_client.close())
        self._loop.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

### 5.2 CLI Tool Development (Week 19-20)

#### CLI Architecture
```python
# spotify_mcp_cli/cli.py
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from spotify_mcp_sdk import SpotifyMCP

console = Console()

@click.group()
@click.option('--api-key', envvar='SPOTIFY_MCP_API_KEY', help='API key')
@click.option('--base-url', default='http://localhost:8000', help='Server URL')
@click.pass_context
def cli(ctx, api_key, base_url):
    """Spotify MCP Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['base_url'] = base_url


# Playback commands
@cli.group()
def playback():
    """Playback control commands"""
    pass


@playback.command()
@click.argument('uri')
@click.pass_context
def play(ctx, uri):
    """Play a track, album, or playlist"""
    async def _play():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            await mcp.playback.play(uri=uri)
            console.print(f"[green]✓[/green] Playing: {uri}")

    asyncio.run(_play())


@playback.command()
@click.pass_context
def pause(ctx):
    """Pause playback"""
    async def _pause():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            await mcp.playback.pause()
            console.print("[yellow]⏸[/yellow] Paused")

    asyncio.run(_pause())


@playback.command()
@click.pass_context
def next(ctx):
    """Skip to next track"""
    async def _next():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            await mcp.playback.skip_next()
            console.print("[green]⏭[/green] Skipped to next")

    asyncio.run(_next())


@playback.command()
@click.pass_context
def status(ctx):
    """Show current playback status"""
    async def _status():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            state = await mcp.playback.get_state()

            if not state or not state.get('item'):
                console.print("[yellow]No active playback[/yellow]")
                return

            track = state['item']
            is_playing = state['is_playing']

            # Create rich display
            table = Table(title="Now Playing")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Track", track['name'])
            table.add_row("Artist", ', '.join(a['name'] for a in track['artists']))
            table.add_row("Album", track['album']['name'])
            table.add_row("Status", "▶ Playing" if is_playing else "⏸ Paused")
            table.add_row("Device", state['device']['name'])
            table.add_row("Volume", f"{state['device']['volume_percent']}%")

            console.print(table)

    asyncio.run(_status())


# Search commands
@cli.command()
@click.argument('query')
@click.option('--type', '-t',
              type=click.Choice(['track', 'album', 'artist', 'playlist']),
              default='track',
              help='Type of search')
@click.option('--limit', '-l', default=10, help='Number of results')
@click.pass_context
def search(ctx, query, type, limit):
    """Search for tracks, albums, artists, or playlists"""
    async def _search():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            results = await mcp.search.search(query, types=[type], limit=limit)

            # Display results in table
            table = Table(title=f"Search Results: {query}")

            if type == 'track':
                table.add_column("Track", style="cyan")
                table.add_column("Artist", style="white")
                table.add_column("Album", style="green")
                table.add_column("URI", style="dim")

                for track in results['tracks']['items']:
                    table.add_row(
                        track['name'],
                        ', '.join(a['name'] for a in track['artists']),
                        track['album']['name'],
                        track['uri']
                    )

            elif type == 'artist':
                table.add_column("Artist", style="cyan")
                table.add_column("Popularity", style="white")
                table.add_column("Genres", style="green")
                table.add_column("URI", style="dim")

                for artist in results['artists']['items']:
                    table.add_row(
                        artist['name'],
                        str(artist['popularity']),
                        ', '.join(artist.get('genres', [])[:3]),
                        artist['uri']
                    )

            console.print(table)

    asyncio.run(_search())


# Playlist commands
@cli.group()
def playlist():
    """Playlist management commands"""
    pass


@playlist.command()
@click.argument('name')
@click.option('--description', '-d', help='Playlist description')
@click.option('--public/--private', default=True, help='Public or private')
@click.pass_context
def create(ctx, name, description, public):
    """Create a new playlist"""
    async def _create():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            playlist = await mcp.playlists.create(
                name=name,
                description=description,
                public=public
            )
            console.print(f"[green]✓[/green] Created playlist: {playlist['name']}")
            console.print(f"URI: {playlist['uri']}")

    asyncio.run(_create())


@playlist.command()
@click.argument('playlist_id')
@click.argument('track_uris', nargs=-1)
@click.pass_context
def add(ctx, playlist_id, track_uris):
    """Add tracks to playlist"""
    async def _add():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            with Progress() as progress:
                task = progress.add_task(
                    "[cyan]Adding tracks...",
                    total=len(track_uris)
                )

                await mcp.playlists.add_tracks(playlist_id, list(track_uris))
                progress.update(task, completed=len(track_uris))

            console.print(f"[green]✓[/green] Added {len(track_uris)} tracks")

    asyncio.run(_add())


@playlist.command()
@click.pass_context
def list(ctx):
    """List your playlists"""
    async def _list():
        async with SpotifyMCP(
            api_key=ctx.obj['api_key'],
            base_url=ctx.obj['base_url']
        ) as mcp:
            playlists = await mcp.playlists.get_user_playlists()

            table = Table(title="Your Playlists")
            table.add_column("Name", style="cyan")
            table.add_column("Tracks", style="white")
            table.add_column("Public", style="green")
            table.add_column("URI", style="dim")

            for pl in playlists['items']:
                table.add_row(
                    pl['name'],
                    str(pl['tracks']['total']),
                    "Yes" if pl['public'] else "No",
                    pl['uri']
                )

            console.print(table)

    asyncio.run(_list())


# Interactive mode
@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode"""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter

    session = PromptSession()

    commands = WordCompleter([
        'play', 'pause', 'next', 'previous',
        'search', 'status', 'volume', 'quit'
    ])

    console.print("[bold]Spotify MCP Interactive Mode[/bold]")
    console.print("Type 'quit' to exit\n")

    while True:
        try:
            command = session.prompt('spotify> ', completer=commands)

            if command == 'quit':
                break

            # Parse and execute command
            # ... implementation

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
```

#### Installation
```toml
# spotify-mcp-cli/pyproject.toml
[project]
name = "spotify-mcp-cli"
version = "1.0.0"
description = "Command-line interface for Spotify MCP Server"
dependencies = [
    "spotify-mcp-sdk>=1.0.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "prompt-toolkit>=3.0.0",
]

[project.scripts]
spotify-mcp = "spotify_mcp_cli.cli:cli"
spotify = "spotify_mcp_cli.cli:cli"  # Shorter alias
```

### 5.3 TypeScript/JavaScript SDK (Week 21)

#### SDK Implementation
```typescript
// spotify-mcp-sdk-js/src/client.ts
import axios, { AxiosInstance } from 'axios';

export interface SpotifyMCPOptions {
  apiKey?: string;
  baseURL?: string;
  timeout?: number;
}

export interface Track {
  id: string;
  name: string;
  uri: string;
  artists: Artist[];
  album: Album;
  duration_ms: number;
  explicit: boolean;
  popularity: number;
}

export interface Playlist {
  id: string;
  name: string;
  uri: string;
  description?: string;
  owner: User;
  public: boolean;
  collaborative: boolean;
  tracks: {
    total: number;
  };
}

export class SpotifyMCP {
  private client: AxiosInstance;

  public playback: PlaybackResource;
  public tracks: TrackResource;
  public playlists: PlaylistResource;
  public search: SearchResource;

  constructor(options: SpotifyMCPOptions = {}) {
    const {
      apiKey,
      baseURL = 'http://localhost:8000',
      timeout = 30000
    } = options;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
    });

    // Initialize resources
    this.playback = new PlaybackResource(this.client);
    this.tracks = new TrackResource(this.client);
    this.playlists = new PlaylistResource(this.client);
    this.search = new SearchResource(this.client);
  }
}

class PlaybackResource {
  constructor(private client: AxiosInstance) {}

  /**
   * Start or resume playback
   * @param options - Playback options
   *
   * @example
   * ```typescript
   * await mcp.playback.play({ uri: 'spotify:track:...' });
   * ```
   */
  async play(options?: {
    uri?: string;
    uris?: string[];
    contextUri?: string;
  }): Promise<void> {
    await this.client.post('/playback/play', options);
  }

  /**
   * Pause playback
   */
  async pause(): Promise<void> {
    await this.client.post('/playback/pause');
  }

  /**
   * Skip to next track
   */
  async skipNext(): Promise<void> {
    await this.client.post('/playback/next');
  }

  /**
   * Get current playback state
   */
  async getState(): Promise<any> {
    const response = await this.client.get('/playback/state');
    return response.data;
  }

  /**
   * Set volume
   * @param volume - Volume level (0-100)
   */
  async setVolume(volume: number): Promise<void> {
    await this.client.post('/playback/volume', { volume_percent: volume });
  }
}

class TrackResource {
  constructor(private client: AxiosInstance) {}

  /**
   * Get track by ID
   * @param trackId - Spotify track ID
   *
   * @example
   * ```typescript
   * const track = await mcp.tracks.get('3n3Ppam7vgaVa1iaRUc9Lp');
   * console.log(track.name);
   * ```
   */
  async get(trackId: string): Promise<Track> {
    const response = await this.client.get(`/tracks/${trackId}`);
    return response.data;
  }

  /**
   * Get multiple tracks
   */
  async getMany(trackIds: string[]): Promise<Track[]> {
    const response = await this.client.get('/tracks', {
      params: { ids: trackIds.join(',') }
    });
    return response.data.tracks;
  }

  /**
   * Get audio features for track
   */
  async getAudioFeatures(trackId: string): Promise<any> {
    const response = await this.client.get(`/tracks/${trackId}/audio-features`);
    return response.data;
  }
}

class SearchResource {
  constructor(private client: AxiosInstance) {}

  /**
   * Search for tracks, albums, artists, or playlists
   * @param query - Search query
   * @param options - Search options
   */
  async search(
    query: string,
    options?: {
      types?: ('track' | 'album' | 'artist' | 'playlist')[];
      limit?: number;
    }
  ): Promise<any> {
    const { types = ['track'], limit = 20 } = options || {};

    const response = await this.client.get('/search', {
      params: {
        q: query,
        type: types.join(','),
        limit
      }
    });

    return response.data;
  }

  /**
   * Search for tracks only
   */
  async tracks(query: string, limit: number = 20): Promise<Track[]> {
    const results = await this.search(query, { types: ['track'], limit });
    return results.tracks?.items || [];
  }
}

// Export everything
export * from './models';
export * from './errors';
```

#### React Hooks (Bonus)
```typescript
// spotify-mcp-sdk-js/src/react.ts
import { useState, useEffect, useCallback } from 'react';
import { SpotifyMCP, Track } from './client';

/**
 * React hook for Spotify MCP client
 */
export function useSpotifyMCP(apiKey?: string) {
  const [client] = useState(() => new SpotifyMCP({ apiKey }));
  return client;
}

/**
 * Hook for current playback state
 */
export function useCurrentPlayback(refreshInterval: number = 5000) {
  const mcp = useSpotifyMCP();
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchState = async () => {
      try {
        const playbackState = await mcp.playback.getState();
        setState(playbackState);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchState();
    interval = setInterval(fetchState, refreshInterval);

    return () => clearInterval(interval);
  }, [mcp, refreshInterval]);

  return { state, loading, error };
}

/**
 * Hook for search functionality
 */
export function useSearch() {
  const mcp = useSpotifyMCP();
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const search = useCallback(async (
    query: string,
    types: ('track' | 'album' | 'artist')[] = ['track']
  ) => {
    setLoading(true);
    try {
      const data = await mcp.search.search(query, { types });
      setResults(data);
    } finally {
      setLoading(false);
    }
  }, [mcp]);

  return { results, loading, search };
}

// Example React component
/*
function NowPlaying() {
  const { state, loading } = useCurrentPlayback();

  if (loading) return <div>Loading...</div>;
  if (!state?.item) return <div>Nothing playing</div>;

  const track = state.item;

  return (
    <div>
      <h2>{track.name}</h2>
      <p>{track.artists.map(a => a.name).join(', ')}</p>
      <img src={track.album.images[0]?.url} alt={track.album.name} />
    </div>
  );
}
*/
```

### 5.4 REST API Layer (Week 22)

#### FastAPI REST API
```python
# src/spotify_mcp/api/rest.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import jwt

app = FastAPI(
    title="Spotify MCP REST API",
    version="1.0.0",
    description="REST API wrapper for Spotify MCP Server"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
async def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(401, "Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(401, "Invalid authentication scheme")

        # Verify JWT or API key
        # ... implementation

        return token
    except ValueError:
        raise HTTPException(401, "Invalid authorization header")

# Request/Response models
class PlayRequest(BaseModel):
    uri: Optional[str] = None
    uris: Optional[List[str]] = None
    context_uri: Optional[str] = None

class VolumeRequest(BaseModel):
    volume_percent: int

class SearchParams(BaseModel):
    q: str
    type: str = "track"
    limit: int = 20

# Playback endpoints
@app.post("/playback/play")
async def play(
    request: PlayRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start or resume playback"""
    # Call MCP server tool
    # ... implementation
    return {"status": "playing"}

@app.post("/playback/pause")
async def pause(api_key: str = Depends(verify_api_key)):
    """Pause playback"""
    return {"status": "paused"}

@app.get("/playback/state")
async def get_playback_state(api_key: str = Depends(verify_api_key)):
    """Get current playback state"""
    # ... implementation
    return {}

# Track endpoints
@app.get("/tracks/{track_id}")
async def get_track(track_id: str, api_key: str = Depends(verify_api_key)):
    """Get track by ID"""
    # ... implementation
    return {}

# Search endpoint
@app.get("/search")
async def search(
    q: str,
    type: str = "track",
    limit: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """Search for tracks, albums, artists, or playlists"""
    # ... implementation
    return {}

# OpenAPI docs automatically at /docs
```

---

## 📚 PHASE 6: Documentation & Developer Tools (Weeks 23-28)

**Goal:** World-class documentation and tooling
**Dependencies:** Phase 5 (SDKs to document)
**Deliverables:** Interactive docs, playground, testing tools

### 6.1 Interactive API Documentation (Week 23-24)

#### Docusaurus Site
```jsx
// docs-site/src/pages/index.js
import React from 'react';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';

export default function Home() {
  return (
    <Layout title="Spotify MCP Server">
      <div className="hero">
        <div className="container">
          <h1>Transform Your AI into a Spotify DJ</h1>
          <p>
            Production-grade MCP server with 100% Spotify API coverage
          </p>

          <div className="buttons">
            <a href="/docs/quickstart" className="button button--primary">
              Get Started
            </a>
            <a href="/playground" className="button button--secondary">
              Try Playground
            </a>
          </div>
        </div>
      </div>

      <div className="features">
        <div className="container">
          <div className="row">
            <div className="col col--4">
              <h3>86 Tools</h3>
              <p>Complete Spotify API coverage</p>
            </div>
            <div className="col col--4">
              <h3>Production Ready</h3>
              <p>Enterprise-grade reliability</p>
            </div>
            <div className="col col--4">
              <h3>Developer First</h3>
              <p>SDKs, CLI, and great docs</p>
            </div>
          </div>
        </div>
      </div>

      <div className="code-example">
        <h2>Quick Example</h2>
        <CodeBlock language="python">{`
from spotify_mcp import SpotifyMCP

mcp = SpotifyMCP(api_key="your_key")

# Play a track
mcp.playback.play(uri="spotify:track:...")

# Search
tracks = mcp.search.tracks("Bohemian Rhapsody")

# Create playlist
playlist = mcp.playlists.create("My Playlist")
mcp.playlists.add_tracks(playlist.id, [track.uri for track in tracks])
        `}</CodeBlock>
      </div>
    </Layout>
  );
}
```

### 6.2 API Playground (Week 25)

#### Interactive Playground
```jsx
// docs-site/src/components/Playground.jsx
import React, { useState } from 'react';
import { SpotifyMCP } from 'spotify-mcp-sdk-js';

export default function Playground() {
  const [apiKey, setApiKey] = useState('');
  const [endpoint, setEndpoint] = useState('search');
  const [params, setParams] = useState({ q: 'Beatles', type: 'track' });
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const execute = async () => {
    setLoading(true);
    try {
      const mcp = new SpotifyMCP({ apiKey });

      // Execute based on endpoint
      let result;
      switch (endpoint) {
        case 'search':
          result = await mcp.search.search(params.q, {
            types: [params.type],
            limit: params.limit || 20
          });
          break;
        case 'playback.state':
          result = await mcp.playback.getState();
          break;
        // ... more endpoints
      }

      setResponse(result);
    } catch (error) {
      setResponse({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="playground">
      <div className="config">
        <h3>Configuration</h3>
        <input
          type="password"
          placeholder="API Key"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
        />

        <select value={endpoint} onChange={e => setEndpoint(e.target.value)}>
          <option value="search">Search</option>
          <option value="playback.state">Get Playback State</option>
          <option value="tracks.get">Get Track</option>
          {/* ... more endpoints */}
        </select>

        <h4>Parameters</h4>
        <textarea
          value={JSON.stringify(params, null, 2)}
          onChange={e => setParams(JSON.parse(e.target.value))}
        />

        <button onClick={execute} disabled={loading}>
          {loading ? 'Loading...' : 'Execute'}
        </button>
      </div>

      <div className="response">
        <h3>Response</h3>
        <pre>{JSON.stringify(response, null, 2)}</pre>
      </div>
    </div>
  );
}
```

### 6.3 Testing & Mocking Tools (Week 26-27)

#### Mock Server
```python
# spotify_mcp_testing/mock_server.py
from fastapi import FastAPI
from typing import Dict, Any
import random

app = FastAPI(title="Spotify MCP Mock Server")

# Mock data generators
class MockDataGenerator:
    @staticmethod
    def track(track_id: str = None) -> Dict[str, Any]:
        track_id = track_id or f"mock_track_{random.randint(1000, 9999)}"
        return {
            "id": track_id,
            "name": f"Mock Track {track_id}",
            "uri": f"spotify:track:{track_id}",
            "artists": [{"id": "artist1", "name": "Mock Artist"}],
            "album": {"id": "album1", "name": "Mock Album"},
            "duration_ms": 180000,
            "explicit": False,
            "popularity": 75
        }

    @staticmethod
    def playlist(playlist_id: str = None) -> Dict[str, Any]:
        playlist_id = playlist_id or f"mock_playlist_{random.randint(1000, 9999)}"
        return {
            "id": playlist_id,
            "name": f"Mock Playlist {playlist_id}",
            "uri": f"spotify:playlist:{playlist_id}",
            "description": "A mock playlist",
            "owner": {"id": "user1", "display_name": "Mock User"},
            "public": True,
            "collaborative": False,
            "tracks": {"total": 10}
        }

mock_gen = MockDataGenerator()

# Mock endpoints
@app.get("/tracks/{track_id}")
async def get_track(track_id: str):
    return mock_gen.track(track_id)

@app.get("/search")
async def search(q: str, type: str = "track", limit: int = 20):
    items = [mock_gen.track() for _ in range(limit)]
    return {
        "tracks": {
            "items": items,
            "total": limit,
            "limit": limit,
            "offset": 0
        }
    }

@app.get("/playback/state")
async def get_playback_state():
    return {
        "is_playing": True,
        "item": mock_gen.track(),
        "device": {
            "id": "device1",
            "name": "Mock Device",
            "type": "Computer",
            "volume_percent": 75
        },
        "progress_ms": 60000
    }

# Configurable scenarios
@app.post("/mock/scenario")
async def set_scenario(scenario: Dict[str, Any]):
    """Configure mock responses for specific scenarios"""
    # ... implementation
    pass
```

#### Test Fixtures & Factories
```python
# spotify_mcp_testing/fixtures.py
import pytest
from spotify_mcp import SpotifyMCP

@pytest.fixture
def mock_mcp_server():
    """Start mock server for testing"""
    # ... start mock server
    yield "http://localhost:8001"
    # ... stop mock server

@pytest.fixture
def mcp_client(mock_mcp_server):
    """MCP client pointed at mock server"""
    return SpotifyMCP(
        api_key="mock_key",
        base_url=mock_mcp_server
    )

@pytest.fixture
def sample_track():
    """Sample track data"""
    return {
        "id": "123",
        "name": "Test Track",
        "uri": "spotify:track:123",
        "artists": [{"id": "artist1", "name": "Test Artist"}],
        "album": {"id": "album1", "name": "Test Album"},
        "duration_ms": 180000
    }

# Usage in tests
async def test_play_track(mcp_client, sample_track):
    await mcp_client.playback.play(uri=sample_track['uri'])
    state = await mcp_client.playback.get_state()
    assert state['item']['id'] == sample_track['id']
```

### 6.4 Video Tutorials & Cookbook (Week 28)

#### Cookbook Examples
```markdown
<!-- docs/cookbook/create-workout-playlist.md -->
# Create a Workout Playlist from BPM

This guide shows how to create a workout playlist with high-energy tracks.

## Prerequisites
- Spotify MCP Server running
- Python SDK installed

## Code

```python
from spotify_mcp import SpotifyMCP

mcp = SpotifyMCP(api_key="your_key")

# Search for high-energy tracks
tracks = []

# Search different genres
genres = ['rock', 'electronic', 'hip-hop']
for genre in genres:
    results = mcp.search.search(f"genre:{genre}", types=['track'], limit=50)
    tracks.extend(results['tracks']['items'])

# Filter by audio features
workout_tracks = []
for track in tracks:
    features = mcp.tracks.get_audio_features(track['id'])

    # High energy, fast tempo
    if features['energy'] > 0.7 and features['tempo'] > 120:
        workout_tracks.append(track)

# Create playlist
playlist = mcp.playlists.create(
    name="High Energy Workout",
    description="Auto-generated workout playlist with BPM > 120"
)

# Add tracks
track_uris = [t['uri'] for t in workout_tracks[:50]]
mcp.playlists.add_tracks(playlist['id'], track_uris)

print(f"Created playlist: {playlist['external_urls']['spotify']}")
```

## Explanation

1. Search for tracks across multiple genres
2. Get audio features for each track
3. Filter by energy (>0.7) and tempo (>120 BPM)
4. Create a new playlist
5. Add the high-energy tracks

## Next Steps

- Add more genre variety
- Sort by tempo for gradual intensity increase
- Schedule daily playlist updates
```

---

**Continue to Part 3 for AI/ML, Analytics, Automation, Enterprise, and Cloud phases?**

This is comprehensive - we're at ~150KB of detailed implementation plans. Should I:
1. ✅ Continue with remaining phases (7-15)
2. ✅ Start implementing Phase 1 now
3. ✅ Create a condensed summary roadmap

What's your preference?

"""Search and discovery tools for Spotify."""

from typing import Optional, List, Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def search(client: SpotifyClient, query: str, search_type: str = "track", 
           limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Search for tracks, albums, artists, or playlists.
    
    Args:
        query: Search query
        search_type: Type to search for - "track", "album", "artist", or "playlist"
        limit: Maximum number of results (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        Search results with items and pagination info
    """
    valid_types = ["track", "album", "artist", "playlist"]
    if search_type not in valid_types:
        raise ValueError(f"search_type must be one of: {', '.join(valid_types)}")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.search(q=query, limit=limit, offset=offset, type=search_type)
    
    # Format results based on type
    key = f"{search_type}s"
    items = results.get(key, {}).get("items", [])
    total = results.get(key, {}).get("total", 0)
    
    formatted_items = []
    
    if search_type == "track":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in item.get("artists", [])],
                "album": {
                    "name": item.get("album", {}).get("name"),
                    "uri": item.get("album", {}).get("uri"),
                },
                "duration_ms": item.get("duration_ms"),
                "explicit": item.get("explicit", False),
                "popularity": item.get("popularity", 0)
            }
            for item in items
        ]
    elif search_type == "album":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in item.get("artists", [])],
                "release_date": item.get("release_date"),
                "total_tracks": item.get("total_tracks"),
                "album_type": item.get("album_type")
            }
            for item in items
        ]
    elif search_type == "artist":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "genres": item.get("genres", []),
                "popularity": item.get("popularity", 0),
                "followers": item.get("followers", {}).get("total", 0)
            }
            for item in items
        ]
    elif search_type == "playlist":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "owner": {
                    "display_name": item.get("owner", {}).get("display_name"),
                    "id": item.get("owner", {}).get("id")
                },
                "description": item.get("description"),
                "total_tracks": item.get("tracks", {}).get("total", 0),
                "public": item.get("public", False)
            }
            for item in items
        ]
    
    return {
        "query": query,
        "type": search_type,
        "items": formatted_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def get_recommendations(client: SpotifyClient, 
                       seed_artists: Optional[List[str]] = None,
                       seed_tracks: Optional[List[str]] = None,
                       seed_genres: Optional[List[str]] = None,
                       limit: int = 20,
                       target_acousticness: Optional[float] = None,
                       target_danceability: Optional[float] = None,
                       target_energy: Optional[float] = None,
                       target_instrumentalness: Optional[float] = None,
                       target_popularity: Optional[int] = None,
                       target_valence: Optional[float] = None,
                       min_tempo: Optional[float] = None,
                       max_tempo: Optional[float] = None) -> Dict[str, Any]:
    """
    Get track recommendations based on seed artists, tracks, and/or genres.
    
    Args:
        seed_artists: List of artist IDs or URIs (up to 5 total seeds)
        seed_tracks: List of track IDs or URIs (up to 5 total seeds)
        seed_genres: List of genre names (up to 5 total seeds)
        limit: Number of recommendations (1-100, default 20)
        target_acousticness: Target acousticness (0.0-1.0)
        target_danceability: Target danceability (0.0-1.0)
        target_energy: Target energy (0.0-1.0)
        target_instrumentalness: Target instrumentalness (0.0-1.0)
        target_popularity: Target popularity (0-100)
        target_valence: Target valence/positivity (0.0-1.0)
        min_tempo: Minimum tempo in BPM
        max_tempo: Maximum tempo in BPM
    
    Returns:
        List of recommended tracks
    
    Note: You must provide at least one seed (artist, track, or genre).
    Total seeds cannot exceed 5.
    """
    # Validate seeds
    seed_artists = seed_artists or []
    seed_tracks = seed_tracks or []
    seed_genres = seed_genres or []
    
    # Extract IDs from URIs if needed
    seed_artists = [s.split(":")[-1] if ":" in s else s for s in seed_artists]
    seed_tracks = [s.split(":")[-1] if ":" in s else s for s in seed_tracks]
    
    total_seeds = len(seed_artists) + len(seed_tracks) + len(seed_genres)
    
    if total_seeds == 0:
        raise ValueError("At least one seed (artist, track, or genre) is required")
    
    if total_seeds > 5:
        raise ValueError("Total number of seeds cannot exceed 5")
    
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    
    # Build kwargs for optional parameters
    kwargs = {}
    if target_acousticness is not None:
        kwargs["target_acousticness"] = target_acousticness
    if target_danceability is not None:
        kwargs["target_danceability"] = target_danceability
    if target_energy is not None:
        kwargs["target_energy"] = target_energy
    if target_instrumentalness is not None:
        kwargs["target_instrumentalness"] = target_instrumentalness
    if target_popularity is not None:
        kwargs["target_popularity"] = target_popularity
    if target_valence is not None:
        kwargs["target_valence"] = target_valence
    if min_tempo is not None:
        kwargs["min_tempo"] = min_tempo
    if max_tempo is not None:
        kwargs["max_tempo"] = max_tempo
    
    results = client.recommendations(
        seed_artists=seed_artists if seed_artists else None,
        seed_tracks=seed_tracks if seed_tracks else None,
        seed_genres=seed_genres if seed_genres else None,
        limit=limit,
        **kwargs
    )
    
    tracks = results.get("tracks", [])
    
    return {
        "seeds": {
            "artists": seed_artists,
            "tracks": seed_tracks,
            "genres": seed_genres
        },
        "recommendations": [
            {
                "name": track["name"],
                "uri": track["uri"],
                "id": track["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in track.get("artists", [])],
                "album": {
                    "name": track.get("album", {}).get("name"),
                    "uri": track.get("album", {}).get("uri"),
                },
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit", False),
                "popularity": track.get("popularity", 0)
            }
            for track in tracks
        ],
        "total": len(tracks)
    }


# Tool definitions for MCP
SEARCH_TOOLS = [
    {
        "name": "search",
        "description": "Search for tracks, albums, artists, or playlists on Spotify.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Bohemian Rhapsody', 'The Beatles', 'rock playlist')"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["track", "album", "artist", "playlist"],
                    "description": "Type of item to search for",
                    "default": "track"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination",
                    "minimum": 0,
                    "default": 0
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get track recommendations based on seed artists, tracks, and/or genres. You can also tune recommendations with audio features.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed_artists": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of artist IDs or URIs (up to 5 total seeds)"
                },
                "seed_tracks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs (up to 5 total seeds)"
                },
                "seed_genres": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of genre names like 'rock', 'pop', 'jazz' (up to 5 total seeds)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recommendations (1-100)",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "target_acousticness": {
                    "type": "number",
                    "description": "Target acousticness (0.0 = not acoustic, 1.0 = very acoustic)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "target_danceability": {
                    "type": "number",
                    "description": "Target danceability (0.0 = not danceable, 1.0 = very danceable)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "target_energy": {
                    "type": "number",
                    "description": "Target energy (0.0 = low energy, 1.0 = high energy)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "target_instrumentalness": {
                    "type": "number",
                    "description": "Target instrumentalness (0.0 = vocal, 1.0 = instrumental)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "target_popularity": {
                    "type": "integer",
                    "description": "Target popularity (0 = niche, 100 = mainstream)",
                    "minimum": 0,
                    "maximum": 100
                },
                "target_valence": {
                    "type": "number",
                    "description": "Target valence/positivity (0.0 = sad, 1.0 = happy)",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "min_tempo": {
                    "type": "number",
                    "description": "Minimum tempo in BPM"
                },
                "max_tempo": {
                    "type": "number",
                    "description": "Maximum tempo in BPM"
                }
            }
        }
    }
]

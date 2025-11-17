"""Track operations and audio analysis tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_track(client: SpotifyClient, track_id: str, market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a track.
    
    Args:
        track_id: Track ID or URI
        market: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
    
    Returns:
        Track details
    """
    # Extract ID from URI if needed
    track_id = track_id.split(":")[-1] if ":" in track_id else track_id
    
    result = client.track(track_id=track_id, market=market)
    
    return {
        "success": True,
        "track": {
            "id": result.get("id"),
            "uri": result.get("uri"),
            "name": result.get("name"),
            "artists": [
                {"name": a["name"], "id": a["id"], "uri": a["uri"]}
                for a in result.get("artists", [])
            ],
            "album": {
                "name": result.get("album", {}).get("name"),
                "id": result.get("album", {}).get("id"),
                "uri": result.get("album", {}).get("uri"),
                "release_date": result.get("album", {}).get("release_date")
            },
            "duration_ms": result.get("duration_ms"),
            "explicit": result.get("explicit", False),
            "popularity": result.get("popularity", 0),
            "track_number": result.get("track_number"),
            "disc_number": result.get("disc_number", 1),
            "external_urls": result.get("external_urls", {}),
            "preview_url": result.get("preview_url")
        }
    }


def get_several_tracks(client: SpotifyClient, track_ids: List[str], 
                      market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about multiple tracks.
    
    Args:
        track_ids: List of track IDs or URIs (up to 50)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        List of track details
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    result = client.tracks(track_ids=track_ids, market=market)
    
    tracks = []
    for track in result.get("tracks", []):
        if track:  # Some might be None if not available
            tracks.append({
                "id": track.get("id"),
                "uri": track.get("uri"),
                "name": track.get("name"),
                "artists": [
                    {"name": a["name"], "id": a["id"]}
                    for a in track.get("artists", [])
                ],
                "album": {
                    "name": track.get("album", {}).get("name"),
                    "id": track.get("album", {}).get("id")
                },
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit", False),
                "popularity": track.get("popularity", 0)
            })
    
    return {
        "success": True,
        "tracks": tracks,
        "total": len(tracks)
    }


def get_tracks_audio_features(client: SpotifyClient, track_ids: List[str]) -> Dict[str, Any]:
    """
    Get audio features for multiple tracks (tempo, energy, danceability, etc.).
    
    Args:
        track_ids: List of track IDs or URIs (up to 100)
    
    Returns:
        List of audio features for each track
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 100:
        raise ValueError("Cannot retrieve audio features for more than 100 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    results = client.audio_features(track_ids=track_ids)
    
    features = []
    for feature in results:
        if feature:  # Some might be None if not available
            features.append({
                "id": feature.get("id"),
                "uri": feature.get("uri"),
                "acousticness": feature.get("acousticness"),
                "danceability": feature.get("danceability"),
                "energy": feature.get("energy"),
                "instrumentalness": feature.get("instrumentalness"),
                "key": feature.get("key"),
                "liveness": feature.get("liveness"),
                "loudness": feature.get("loudness"),
                "mode": feature.get("mode"),
                "speechiness": feature.get("speechiness"),
                "tempo": feature.get("tempo"),
                "time_signature": feature.get("time_signature"),
                "valence": feature.get("valence"),
                "duration_ms": feature.get("duration_ms")
            })
    
    return {
        "success": True,
        "audio_features": features,
        "total": len(features)
    }


def get_track_audio_features(client: SpotifyClient, track_id: str) -> Dict[str, Any]:
    """
    Get audio features for a single track (tempo, energy, danceability, etc.).
    
    Args:
        track_id: Track ID or URI
    
    Returns:
        Audio features for the track
    """
    # Extract ID from URI if needed
    track_id = track_id.split(":")[-1] if ":" in track_id else track_id
    
    # Use the batch method with single track
    result = client.audio_features(track_ids=[track_id])
    
    if not result or not result[0]:
        raise ValueError(f"No audio features available for track: {track_id}")
    
    feature = result[0]
    
    return {
        "success": True,
        "track_id": feature.get("id"),
        "audio_features": {
            "acousticness": feature.get("acousticness"),
            "danceability": feature.get("danceability"),
            "energy": feature.get("energy"),
            "instrumentalness": feature.get("instrumentalness"),
            "key": feature.get("key"),
            "liveness": feature.get("liveness"),
            "loudness": feature.get("loudness"),
            "mode": feature.get("mode"),
            "speechiness": feature.get("speechiness"),
            "tempo": feature.get("tempo"),
            "time_signature": feature.get("time_signature"),
            "valence": feature.get("valence"),
            "duration_ms": feature.get("duration_ms")
        }
    }


def get_track_audio_analysis(client: SpotifyClient, track_id: str) -> Dict[str, Any]:
    """
    Get detailed audio analysis for a track (bars, beats, sections, segments).
    
    Args:
        track_id: Track ID or URI
    
    Returns:
        Detailed audio analysis including bars, beats, sections, and segments
    """
    # Extract ID from URI if needed
    track_id = track_id.split(":")[-1] if ":" in track_id else track_id
    
    result = client.audio_analysis(track_id=track_id)
    
    return {
        "success": True,
        "track_id": track_id,
        "analysis": {
            "duration": result.get("track", {}).get("duration"),
            "sample_rate": result.get("track", {}).get("sample_rate"),
            "tempo": result.get("track", {}).get("tempo"),
            "tempo_confidence": result.get("track", {}).get("tempo_confidence"),
            "time_signature": result.get("track", {}).get("time_signature"),
            "time_signature_confidence": result.get("track", {}).get("time_signature_confidence"),
            "key": result.get("track", {}).get("key"),
            "key_confidence": result.get("track", {}).get("key_confidence"),
            "mode": result.get("track", {}).get("mode"),
            "mode_confidence": result.get("track", {}).get("mode_confidence"),
            "loudness": result.get("track", {}).get("loudness"),
            "bars": result.get("bars", []),
            "beats": result.get("beats", []),
            "sections": result.get("sections", []),
            "segments": result.get("segments", []),
            "tatums": result.get("tatums", [])
        },
        "bars_count": len(result.get("bars", [])),
        "beats_count": len(result.get("beats", [])),
        "sections_count": len(result.get("sections", [])),
        "segments_count": len(result.get("segments", []))
    }


# Tool definitions for MCP
TRACK_TOOLS = [
    {
        "name": "get_track",
        "description": "Get detailed information about a track including artists, album, duration, and popularity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_id": {
                    "type": "string",
                    "description": "Track ID or URI (e.g., 'spotify:track:xxx' or 'trackid')"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')"
                }
            },
            "required": ["track_id"]
        }
    },
    {
        "name": "get_several_tracks",
        "description": "Get detailed information about multiple tracks at once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs (e.g., ['spotify:track:xxx']). Maximum 50 tracks.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                }
            },
            "required": ["track_ids"]
        }
    },
    {
        "name": "get_tracks_audio_features",
        "description": "Get audio features (tempo, energy, danceability, valence, etc.) for multiple tracks. Perfect for analyzing music characteristics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs. Maximum 100 tracks.",
                    "minItems": 1,
                    "maxItems": 100
                }
            },
            "required": ["track_ids"]
        }
    },
    {
        "name": "get_track_audio_features",
        "description": "Get audio features for a single track including tempo, energy, danceability, acousticness, valence, and more.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_id": {
                    "type": "string",
                    "description": "Track ID or URI"
                }
            },
            "required": ["track_id"]
        }
    },
    {
        "name": "get_track_audio_analysis",
        "description": "Get detailed low-level audio analysis for a track including bars, beats, sections, segments, and tatums. Useful for advanced music analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_id": {
                    "type": "string",
                    "description": "Track ID or URI"
                }
            },
            "required": ["track_id"]
        }
    }
]

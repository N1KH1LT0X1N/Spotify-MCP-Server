"""
Tool definitions for composite tools.

Composite tools combine multiple Spotify operations for better user experience.
"""

COMPOSITE_TOOL_DEFINITIONS = [
    {
        "name": "create_playlist_with_tracks",
        "description": "Create a new playlist and immediately add tracks to it in one operation. Supports up to 100 tracks per request.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID who will own the playlist"
                },
                "name": {
                    "type": "string",
                    "description": "Name for the new playlist"
                },
                "tracks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify track URIs to add to the playlist"
                },
                "public": {
                    "type": "boolean",
                    "description": "Whether the playlist should be public (default: true)",
                    "default": True
                },
                "description": {
                    "type": "string",
                    "description": "Optional description for the playlist"
                }
            },
            "required": ["user_id", "name", "tracks"]
        }
    },
    {
        "name": "get_artist_full_profile",
        "description": "Get complete artist information including bio, top 10 tracks, and up to 20 albums in one call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artist_id": {
                    "type": "string",
                    "description": "Spotify artist ID"
                }
            },
            "required": ["artist_id"]
        }
    },
    {
        "name": "search_and_create_playlist",
        "description": "Search for tracks/albums/artists and automatically create a playlist from the results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'jazz music', 'artist:Adele', 'track:Bohemian Rhapsody')"
                },
                "user_id": {
                    "type": "string",
                    "description": "User ID to create the playlist for"
                },
                "playlist_name": {
                    "type": "string",
                    "description": "Name for the created playlist"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to include (default: 20, max: 50)",
                    "default": 20
                },
                "search_type": {
                    "type": "string",
                    "enum": ["track", "album", "artist"],
                    "description": "Type of content to search for (default: track)",
                    "default": "track"
                }
            },
            "required": ["query", "user_id", "playlist_name"]
        }
    },
    {
        "name": "get_listening_summary",
        "description": "Get a comprehensive summary of user's listening habits including top tracks, artists, and recently played.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "time_range": {
                    "type": "string",
                    "enum": ["short_term", "medium_term", "long_term"],
                    "description": "Time range for analysis. short_term: last 4 weeks, medium_term: last 6 months, long_term: all time (default: medium_term)",
                    "default": "medium_term"
                }
            },
            "required": []
        }
    },
    {
        "name": "save_multiple_items",
        "description": "Save multiple types of items to user's library (tracks, albums, follow artists) in one operation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Track IDs to save to library"
                },
                "album_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Album IDs to save to library"
                },
                "artist_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Artist IDs to follow"
                }
            },
            "required": []
        }
    },
    {
        "name": "compare_user_libraries",
        "description": "Compare current user's library with another user's public profile to see overlapping interests.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Spotify user ID to compare with"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of playlists to compare (default: 50)",
                    "default": 50
                }
            },
            "required": ["user_id"]
        }
    }
]

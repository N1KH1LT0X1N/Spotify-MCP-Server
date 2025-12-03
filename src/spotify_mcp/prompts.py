"""
MCP Prompts for Spotify interactions.

Prompts are pre-defined conversation templates that help users discover
and use Spotify MCP Server capabilities more easily.
"""

from typing import Any, Dict, List, Optional


class SpotifyPrompts:
    """Handler for Spotify MCP prompts."""

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        """
        List all available prompts.

        Returns:
            List of prompt definitions
        """
        return [
            {
                "name": "discover_new_music",
                "description": "Discover new music based on your preferences",
                "arguments": [
                    {
                        "name": "mood",
                        "description": "The mood or genre you're interested in (e.g., 'chill', 'energetic', 'jazz')",
                        "required": False
                    }
                ]
            },
            {
                "name": "create_playlist",
                "description": "Create a custom playlist with specific criteria",
                "arguments": [
                    {
                        "name": "theme",
                        "description": "Theme or purpose of the playlist (e.g., 'workout', 'study', 'party')",
                        "required": False
                    }
                ]
            },
            {
                "name": "whats_playing",
                "description": "Get detailed information about what's currently playing",
                "arguments": []
            },
            {
                "name": "control_playback",
                "description": "Control music playback with common commands",
                "arguments": [
                    {
                        "name": "action",
                        "description": "Playback action (e.g., 'play', 'pause', 'skip', 'volume')",
                        "required": False
                    }
                ]
            },
            {
                "name": "manage_library",
                "description": "Organize and manage your Spotify library",
                "arguments": [
                    {
                        "name": "task",
                        "description": "Library management task (e.g., 'organize', 'cleanup', 'discover')",
                        "required": False
                    }
                ]
            },
            {
                "name": "find_similar",
                "description": "Find music similar to an artist or track",
                "arguments": [
                    {
                        "name": "reference",
                        "description": "Artist name or track name to find similar music for",
                        "required": True
                    }
                ]
            },
            {
                "name": "analyze_listening_habits",
                "description": "Analyze your listening habits and get insights",
                "arguments": [
                    {
                        "name": "timeframe",
                        "description": "Time period to analyze (e.g., 'short_term', 'medium_term', 'long_term')",
                        "required": False
                    }
                ]
            },
            {
                "name": "explore_artist",
                "description": "Deep dive into an artist's discography and related artists",
                "arguments": [
                    {
                        "name": "artist_name",
                        "description": "Name of the artist to explore",
                        "required": True
                    }
                ]
            }
        ]

    @staticmethod
    def get(name: str, arguments: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get a prompt by name with optional arguments.

        Args:
            name: Prompt name
            arguments: Optional arguments for the prompt

        Returns:
            Prompt message with filled arguments

        Raises:
            ValueError: If prompt name is invalid
        """
        arguments = arguments or {}

        prompts = {
            "discover_new_music": SpotifyPrompts._discover_new_music,
            "create_playlist": SpotifyPrompts._create_playlist,
            "whats_playing": SpotifyPrompts._whats_playing,
            "control_playback": SpotifyPrompts._control_playback,
            "manage_library": SpotifyPrompts._manage_library,
            "find_similar": SpotifyPrompts._find_similar,
            "analyze_listening_habits": SpotifyPrompts._analyze_listening_habits,
            "explore_artist": SpotifyPrompts._explore_artist,
        }

        if name not in prompts:
            raise ValueError(f"Unknown prompt: {name}")

        return prompts[name](arguments)

    # Prompt templates

    @staticmethod
    def _discover_new_music(args: Dict[str, str]) -> Dict[str, Any]:
        """Discover new music prompt."""
        mood = args.get("mood", "something new")

        return {
            "description": "Discover new music workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to discover {mood} music. Can you help me find some great tracks?\n\n"
                                f"Here's what I'd like:\n"
                                f"1. Search for popular {mood} playlists and artists\n"
                                f"2. Look at my top artists and tracks for inspiration\n"
                                f"3. Suggest some albums or playlists I should check out\n"
                                f"4. Check what's trending in new releases\n\n"
                                f"Feel free to use resources like my current playback state and recently "
                                f"played tracks for context!"
                    }
                }
            ]
        }

    @staticmethod
    def _create_playlist(args: Dict[str, str]) -> Dict[str, Any]:
        """Create playlist prompt."""
        theme = args.get("theme", "a custom")

        return {
            "description": "Create custom playlist workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to create {theme} playlist. Can you help me build it?\n\n"
                                f"Steps:\n"
                                f"1. Create a new playlist with an appropriate name and description\n"
                                f"2. Search for songs that fit the theme\n"
                                f"3. Add the best tracks to the playlist\n"
                                f"4. Make sure there's a good variety and flow\n\n"
                                f"Aim for around 20-30 songs that work well together!"
                    }
                }
            ]
        }

    @staticmethod
    def _whats_playing(args: Dict[str, str]) -> Dict[str, Any]:
        """What's playing prompt."""
        return {
            "description": "Current playback information",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "What's currently playing on my Spotify? Please show me:\n\n"
                                "- Track name and artist\n"
                                "- Album and release year\n"
                                "- Playback device and volume\n"
                                "- Shuffle and repeat settings\n"
                                "- Playback progress\n\n"
                                "Use the spotify://playback/current resource for real-time data!"
                    }
                }
            ]
        }

    @staticmethod
    def _control_playback(args: Dict[str, str]) -> Dict[str, Any]:
        """Control playback prompt."""
        action = args.get("action", "control my music")

        return {
            "description": "Playback control workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to {action}. Here are common playback controls:\n\n"
                                f"**Playback:**\n"
                                f"- Play/pause\n"
                                f"- Skip to next/previous track\n"
                                f"- Seek to a specific position\n\n"
                                f"**Volume:**\n"
                                f"- Adjust volume (0-100%)\n\n"
                                f"**Modes:**\n"
                                f"- Toggle shuffle\n"
                                f"- Set repeat mode (track/context/off)\n\n"
                                f"**Devices:**\n"
                                f"- Switch playback device\n"
                                f"- View available devices\n\n"
                                f"What would you like to do?"
                    }
                }
            ]
        }

    @staticmethod
    def _manage_library(args: Dict[str, str]) -> Dict[str, Any]:
        """Manage library prompt."""
        task = args.get("task", "organize my music")

        return {
            "description": "Library management workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to {task}. Here's what I can do with my library:\n\n"
                                f"**View:**\n"
                                f"- Saved tracks (liked songs)\n"
                                f"- Saved albums\n"
                                f"- Playlists\n"
                                f"- Recently played\n\n"
                                f"**Manage:**\n"
                                f"- Save/remove tracks\n"
                                f"- Save/remove albums\n"
                                f"- Create/edit playlists\n"
                                f"- Follow/unfollow artists\n\n"
                                f"**Analyze:**\n"
                                f"- Top tracks and artists\n"
                                f"- Listening habits\n"
                                f"- Genre preferences\n\n"
                                f"Use resources like spotify://library/saved-tracks and spotify://playlists "
                                f"to view current library state!"
                    }
                }
            ]
        }

    @staticmethod
    def _find_similar(args: Dict[str, str]) -> Dict[str, Any]:
        """Find similar music prompt."""
        reference = args.get("reference", "my favorite artist")

        return {
            "description": "Find similar music workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to find music similar to '{reference}'. Can you help?\n\n"
                                f"Please:\n"
                                f"1. Search for '{reference}' to get the artist/track info\n"
                                f"2. Show me their top tracks and albums\n"
                                f"3. Search for playlists with similar artists\n"
                                f"4. Check their genre to find more artists in that style\n\n"
                                f"I'm looking to expand my music taste while staying in a similar vibe!"
                    }
                }
            ]
        }

    @staticmethod
    def _analyze_listening_habits(args: Dict[str, str]) -> Dict[str, Any]:
        """Analyze listening habits prompt."""
        timeframe = args.get("timeframe", "medium_term")

        timeframe_desc = {
            "short_term": "last 4 weeks",
            "medium_term": "last 6 months",
            "long_term": "several years"
        }.get(timeframe, "last 6 months")

        return {
            "description": "Listening habits analysis",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Analyze my Spotify listening habits from {timeframe_desc}. Please show me:\n\n"
                                f"**Top Content:**\n"
                                f"- My top 10 artists\n"
                                f"- My top 10 tracks\n"
                                f"- Genre breakdown\n\n"
                                f"**Insights:**\n"
                                f"- Listening patterns\n"
                                f"- Musical preferences\n"
                                f"- Discovery vs. familiar\n\n"
                                f"**Recently:**\n"
                                f"- Recently played tracks\n"
                                f"- Current favorite playlists\n\n"
                                f"Use get_top_items with time_range='{timeframe}' and "
                                f"spotify://library/recent resource!"
                    }
                }
            ]
        }

    @staticmethod
    def _explore_artist(args: Dict[str, str]) -> Dict[str, Any]:
        """Explore artist prompt."""
        artist_name = args.get("artist_name", "an artist")

        return {
            "description": "Artist exploration workflow",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"I want to explore everything about {artist_name}. Please help me discover:\n\n"
                                f"**Artist Info:**\n"
                                f"- Bio and background\n"
                                f"- Popularity and followers\n"
                                f"- Genres\n\n"
                                f"**Music:**\n"
                                f"- Top tracks\n"
                                f"- Albums and EPs (chronological)\n"
                                f"- Featured tracks\n\n"
                                f"**Discovery:**\n"
                                f"- Search for similar genre playlists\n"
                                f"- Collaborative tracks and features\n"
                                f"- Artists with similar styles\n\n"
                                f"Give me a comprehensive overview of {artist_name}'s musical universe!"
                    }
                }
            ]
        }

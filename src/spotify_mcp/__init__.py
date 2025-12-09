"""Spotify MCP Server - Control Spotify through AI.

A production-ready Model Context Protocol server that brings Spotify's full power
to AI assistants. Control playback, discover music, manage playlists, and explore
your library—all through natural conversation.

🎵 75 Production-Ready Tools:
- Playback Control (12 tools) - Play, pause, skip, volume, shuffle, repeat, seek
- Playlists (12 tools) - Create, modify, manage, upload covers
- Albums (8 tools) - Browse, save, discover new releases
- User Profile (8 tools) - Top tracks/artists, following, profile management
- Shows/Podcasts (7 tools) - Discover and manage podcast content
- Episodes (6 tools) - Save and track podcast episodes
- Artists (4 tools) - Artist details, albums, top tracks
- Library Management (4 tools) - Saved tracks operations
- Categories (2 tools) - Browse Spotify categories
- Queue (2 tools) - View and manage playback queue
- Tracks (2 tools) - Track details and information
- Search (1 tool) - Universal Spotify search
- Markets (1 tool) - Available market information
- Composite Operations (6 tools) - Multi-step workflows

🔐 Security: OAuth 2.0 with PKCE, automatic token refresh
📊 Resources: 10 dynamic resources for real-time data
🎯 MCP Protocol: Full compliance with 2025-06-18 specification
⚡ FastMCP v3.0: Context injection, structured output, annotations

Note: Audiobooks, Chapters, and Genre Seeds deprecated by Spotify API (Nov 2024).
"""

__version__ = "2.0.0"
__author__ = "N1KH1LT0X1N"
__mcp_version__ = "2025-06-18"
__fastmcp_version__ = "3.0"

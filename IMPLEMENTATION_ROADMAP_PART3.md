# 🚀 Implementation Roadmap - Part 3: Intelligence, Enterprise & Scale

## 🤖 PHASE 7: AI/ML Intelligence Features (Weeks 29-40)

**Goal:** Add AI-powered features that create unique value
**Dependencies:** Phase 2 (caching for performance), Phase 5 (SDK)
**Deliverables:** Smart recommendations, NLP, predictive features

### 7.1 Audio Feature Analysis Engine (Week 29-30)

#### Feature Extraction & Analysis
```python
# src/spotify_mcp/intelligence/audio_analysis.py
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class AudioFeatureAnalyzer:
    """Analyze and cluster tracks by audio features"""

    FEATURE_KEYS = [
        'danceability', 'energy', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness',
        'valence', 'tempo', 'loudness'
    ]

    def __init__(self, spotify_client):
        self.client = spotify_client
        self.scaler = StandardScaler()

    async def analyze_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Deep analysis of playlist characteristics"""

        # Get all tracks
        tracks = await self._get_playlist_tracks(playlist_id)

        # Get audio features
        features_list = []
        for track in tracks:
            features = await self.client.get_track_audio_features(track['id'])
            features_list.append(features)

        # Calculate statistics
        stats = self._calculate_stats(features_list)

        # Identify mood
        mood = self._identify_mood(stats)

        # Find clusters
        clusters = self._cluster_tracks(features_list, n_clusters=3)

        return {
            'statistics': stats,
            'mood': mood,
            'clusters': clusters,
            'recommendations': await self._get_recommendations(stats)
        }

    def _calculate_stats(self, features_list: List[Dict]) -> Dict:
        """Calculate statistical summary of features"""
        stats = {}

        for key in self.FEATURE_KEYS:
            values = [f[key] for f in features_list if f.get(key) is not None]

            stats[key] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'median': np.median(values)
            }

        return stats

    def _identify_mood(self, stats: Dict) -> str:
        """Identify overall mood/vibe of playlist"""

        valence = stats['valence']['mean']
        energy = stats['energy']['mean']
        danceability = stats['danceability']['mean']

        # Decision tree for mood
        if valence > 0.7 and energy > 0.7:
            return 'euphoric'
        elif valence > 0.6 and danceability > 0.6:
            return 'upbeat'
        elif energy < 0.4 and valence < 0.4:
            return 'melancholic'
        elif energy < 0.3:
            return 'chill'
        elif energy > 0.8:
            return 'intense'
        elif valence > 0.5:
            return 'positive'
        else:
            return 'neutral'

    def _cluster_tracks(self, features_list: List[Dict], n_clusters: int = 3) -> List[Dict]:
        """Cluster tracks by audio features"""

        # Extract feature vectors
        X = np.array([
            [f[key] for key in self.FEATURE_KEYS]
            for f in features_list
        ])

        # Normalize
        X_scaled = self.scaler.fit_transform(X)

        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(X_scaled)

        # Group by cluster
        clusters = []
        for i in range(n_clusters):
            cluster_indices = np.where(labels == i)[0]
            cluster_features = X_scaled[cluster_indices]

            # Get centroid characteristics
            centroid = kmeans.cluster_centers_[i]
            characteristics = self._describe_cluster(centroid)

            clusters.append({
                'id': i,
                'size': len(cluster_indices),
                'track_indices': cluster_indices.tolist(),
                'characteristics': characteristics
            })

        return clusters

    def _describe_cluster(self, centroid: np.ndarray) -> Dict:
        """Describe cluster characteristics in human terms"""

        # Denormalize (approximate)
        features = dict(zip(self.FEATURE_KEYS, centroid))

        description = []

        if features['energy'] > 0.5:
            description.append('high energy')
        else:
            description.append('low energy')

        if features['danceability'] > 0.5:
            description.append('danceable')

        if features['valence'] > 0.5:
            description.append('positive')
        else:
            description.append('melancholic')

        if features['acousticness'] > 0.5:
            description.append('acoustic')

        if features['instrumentalness'] > 0.5:
            description.append('instrumental')

        return {
            'description': ', '.join(description),
            'features': features
        }

    async def _get_recommendations(self, stats: Dict) -> List[str]:
        """Get recommendations based on audio features"""

        # Use Spotify's recommendation API with target features
        target_features = {
            f'target_{key}': stats[key]['mean']
            for key in self.FEATURE_KEYS
        }

        recommendations = await self.client.get_recommendations(
            seed_tracks=[],  # Use seed genres instead
            limit=20,
            **target_features
        )

        return recommendations['tracks']
```

### 7.2 Smart Playlist Generation (Week 31-32)

#### ML-Powered Playlist Creator
```python
# src/spotify_mcp/intelligence/smart_playlists.py
from datetime import datetime, time
from typing import List, Dict, Optional
import random

class SmartPlaylistGenerator:
    """Generate playlists using ML and contextual awareness"""

    def __init__(self, spotify_client, audio_analyzer):
        self.client = spotify_client
        self.analyzer = audio_analyzer

    async def create_contextual_playlist(
        self,
        context: str,
        duration_minutes: int = 60,
        user_preferences: Optional[Dict] = None
    ) -> Dict:
        """
        Create playlist based on context

        Contexts:
        - workout: High energy, fast tempo
        - focus: Instrumental, moderate energy
        - sleep: Low energy, calm
        - party: High danceability, popular tracks
        - commute: Varied, user's top tracks
        """

        # Get context parameters
        params = self._get_context_parameters(context)

        # Add user preferences
        if user_preferences:
            params.update(user_preferences)

        # Calculate number of tracks needed
        avg_track_duration = 3.5  # minutes
        num_tracks = int(duration_minutes / avg_track_duration)

        # Get seed tracks from user's library
        seeds = await self._get_seed_tracks(context)

        # Generate recommendations
        tracks = []
        for seed_batch in self._batch_seeds(seeds, 5):
            recommendations = await self.client.get_recommendations(
                seed_tracks=[s['id'] for s in seed_batch],
                limit=20,
                **params
            )
            tracks.extend(recommendations['tracks'])

        # Filter and sort
        tracks = await self._filter_tracks(tracks, context)
        tracks = await self._sort_tracks(tracks, context)

        # Trim to desired length
        tracks = tracks[:num_tracks]

        # Create playlist
        playlist_name = self._generate_playlist_name(context)
        playlist = await self.client.create_playlist(
            name=playlist_name,
            description=f"Auto-generated {context} playlist"
        )

        # Add tracks
        track_uris = [t['uri'] for t in tracks]
        await self.client.add_tracks_to_playlist(playlist['id'], track_uris)

        return {
            'playlist': playlist,
            'tracks': tracks,
            'context': context,
            'analysis': await self.analyzer.analyze_playlist(playlist['id'])
        }

    def _get_context_parameters(self, context: str) -> Dict:
        """Get Spotify API parameters for context"""

        contexts = {
            'workout': {
                'target_energy': 0.8,
                'target_tempo': 140,
                'target_danceability': 0.7,
                'min_energy': 0.6
            },
            'focus': {
                'target_instrumentalness': 0.8,
                'target_energy': 0.5,
                'max_speechiness': 0.1,
                'target_valence': 0.5
            },
            'sleep': {
                'target_energy': 0.2,
                'target_acousticness': 0.7,
                'target_valence': 0.3,
                'max_tempo': 90,
                'max_loudness': -15
            },
            'party': {
                'target_danceability': 0.9,
                'target_energy': 0.8,
                'target_valence': 0.8,
                'min_popularity': 70
            },
            'chill': {
                'target_energy': 0.4,
                'target_valence': 0.6,
                'target_acousticness': 0.6
            },
            'commute': {
                'target_energy': 0.6,
                'target_valence': 0.6
            }
        }

        return contexts.get(context, {})

    async def _get_seed_tracks(self, context: str) -> List[Dict]:
        """Get seed tracks based on context"""

        # Get user's top tracks
        top_tracks = await self.client.get_top_items(
            type='tracks',
            limit=50,
            time_range='medium_term'
        )

        # Filter by context if needed
        seeds = top_tracks['items'][:20]

        return seeds

    async def _filter_tracks(self, tracks: List[Dict], context: str) -> List[Dict]:
        """Filter tracks based on context rules"""

        filtered = []

        for track in tracks:
            # Skip duplicates
            if any(t['id'] == track['id'] for t in filtered):
                continue

            # Context-specific filtering
            if context == 'focus':
                # Skip tracks with lyrics
                features = await self.client.get_track_audio_features(track['id'])
                if features['speechiness'] > 0.2:
                    continue

            filtered.append(track)

        return filtered

    async def _sort_tracks(self, tracks: List[Dict], context: str) -> List[Dict]:
        """Sort tracks for optimal listening experience"""

        if context == 'workout':
            # Sort by tempo for gradual warmup
            features_map = {}
            for track in tracks:
                features = await self.client.get_track_audio_features(track['id'])
                features_map[track['id']] = features

            # Warmup -> Peak -> Cooldown
            tracks_sorted = sorted(
                tracks,
                key=lambda t: features_map[t['id']]['tempo']
            )

            # Rearrange: slow -> fast -> slow
            n = len(tracks_sorted)
            third = n // 3
            return (
                tracks_sorted[:third] +
                list(reversed(tracks_sorted[third:2*third])) +
                tracks_sorted[2*third:]
            )

        elif context == 'party':
            # Most danceable first
            random.shuffle(tracks)  # Some randomness
            return tracks

        else:
            # Default: slight shuffle
            random.shuffle(tracks)
            return tracks

    def _generate_playlist_name(self, context: str) -> str:
        """Generate creative playlist name"""

        now = datetime.now()

        names = {
            'workout': f"Workout Power {now.strftime('%b %d')}",
            'focus': f"Deep Focus {now.strftime('%A')}",
            'sleep': f"Sleep Sounds {now.strftime('%b %d')}",
            'party': f"Party Mix {now.strftime('%Y')}",
            'chill': f"Chill Vibes {now.strftime('%b')}",
            'commute': f"Commute {now.strftime('%b %d')}"
        }

        return names.get(context, f"{context.title()} Playlist")

    async def create_discover_weekly_clone(self) -> Dict:
        """Create a Discover Weekly-style playlist"""

        # Get user's top artists and tracks
        top_artists = await self.client.get_top_items(
            type='artists',
            limit=5,
            time_range='short_term'
        )

        top_tracks = await self.client.get_top_items(
            type='tracks',
            limit=5,
            time_range='short_term'
        )

        # Get related artists
        related_artists = []
        for artist in top_artists['items']:
            related = await self.client.get_artist_related_artists(artist['id'])
            related_artists.extend(related['artists'][:3])

        # Get top tracks from related artists
        discovery_tracks = []
        for artist in related_artists:
            top = await self.client.get_artist_top_tracks(artist['id'])
            discovery_tracks.extend(top['tracks'][:2])

        # Filter out tracks user already knows
        saved_tracks = await self.client.get_saved_tracks(limit=50)
        saved_ids = {t['track']['id'] for t in saved_tracks['items']}

        new_tracks = [
            t for t in discovery_tracks
            if t['id'] not in saved_ids
        ]

        # Create playlist
        playlist = await self.client.create_playlist(
            name=f"Discover Weekly Clone {datetime.now().strftime('%b %d')}",
            description="AI-generated discoveries based on your taste"
        )

        track_uris = [t['uri'] for t in new_tracks[:30]]
        await self.client.add_tracks_to_playlist(playlist['id'], track_uris)

        return {'playlist': playlist, 'tracks': new_tracks[:30]}
```

### 7.3 Natural Language Query Processing (Week 33-35)

#### NLP Integration with Claude
```python
# src/spotify_mcp/intelligence/nlp.py
from anthropic import AsyncAnthropic
import json
from typing import Dict, Any

class NaturalLanguageProcessor:
    """Process natural language music queries"""

    def __init__(self, spotify_client, anthropic_api_key: str):
        self.client = spotify_client
        self.anthropic = AsyncAnthropic(api_key=anthropic_api_key)

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language query and execute

        Examples:
        - "Play something upbeat for my workout"
        - "Find songs like Bohemian Rhapsody but slower"
        - "Create a playlist of acoustic covers"
        - "Remove all sad songs from my playlist"
        """

        # Parse intent using Claude
        intent = await self._parse_intent(query)

        # Execute based on intent
        if intent['type'] == 'play':
            return await self._handle_play(intent)
        elif intent['type'] == 'search':
            return await self._handle_search(intent)
        elif intent['type'] == 'create_playlist':
            return await self._handle_create_playlist(intent)
        elif intent['type'] == 'modify_playlist':
            return await self._handle_modify_playlist(intent)
        else:
            return {'error': 'Could not understand query'}

    async def _parse_intent(self, query: str) -> Dict:
        """Use Claude to parse natural language intent"""

        prompt = f"""
Parse this music-related query into structured intent:

Query: "{query}"

Extract:
1. Intent type (play, search, create_playlist, modify_playlist, get_info)
2. Filters (genre, mood, tempo, energy level, etc.)
3. Target (track, album, artist, playlist)
4. Action parameters

Return as JSON with this structure:
{{
  "type": "intent_type",
  "filters": {{}},
  "target": "target_type",
  "parameters": {{}}
}}

Examples:
- "Play something upbeat" → {{"type": "play", "filters": {{"mood": "upbeat"}}, "target": "track"}}
- "Create a chill playlist" → {{"type": "create_playlist", "filters": {{"mood": "chill"}}}}
"""

        response = await self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        intent = json.loads(response.content[0].text)

        return intent

    async def _handle_play(self, intent: Dict) -> Dict:
        """Handle play intents"""

        filters = intent.get('filters', {})

        # Convert natural language filters to Spotify API parameters
        spotify_params = self._convert_filters_to_spotify_params(filters)

        # Get recommendations
        recommendations = await self.client.get_recommendations(
            limit=20,
            **spotify_params
        )

        # Play first track
        if recommendations['tracks']:
            track = recommendations['tracks'][0]
            await self.client.start_playback(uris=[track['uri']])

            return {
                'action': 'played',
                'track': track,
                'message': f"Playing {track['name']} by {track['artists'][0]['name']}"
            }

        return {'error': 'No matching tracks found'}

    async def _handle_search(self, intent: Dict) -> Dict:
        """Handle search intents"""

        filters = intent.get('filters', {})
        query_parts = []

        # Build search query
        if 'genre' in filters:
            query_parts.append(f"genre:{filters['genre']}")
        if 'artist' in filters:
            query_parts.append(f"artist:{filters['artist']}")
        if 'year' in filters:
            query_parts.append(f"year:{filters['year']}")

        query = ' '.join(query_parts) if query_parts else intent.get('query', '')

        results = await self.client.search(
            query,
            type='track',
            limit=20
        )

        # Apply audio feature filters
        if any(k in filters for k in ['mood', 'energy', 'tempo']):
            results = await self._filter_by_audio_features(
                results['tracks']['items'],
                filters
            )

        return {
            'action': 'search',
            'results': results,
            'query': query
        }

    async def _handle_create_playlist(self, intent: Dict) -> Dict:
        """Handle playlist creation intents"""

        filters = intent.get('filters', {})
        name = intent.get('parameters', {}).get('name', 'AI Generated Playlist')

        # Use smart playlist generator
        from .smart_playlists import SmartPlaylistGenerator
        generator = SmartPlaylistGenerator(self.client, None)

        # Map mood to context
        context = filters.get('mood', 'chill')

        playlist = await generator.create_contextual_playlist(
            context=context,
            duration_minutes=60
        )

        return {
            'action': 'created_playlist',
            'playlist': playlist,
            'message': f"Created playlist '{name}'"
        }

    def _convert_filters_to_spotify_params(self, filters: Dict) -> Dict:
        """Convert NL filters to Spotify API parameters"""

        params = {}

        # Mood mappings
        moods = {
            'happy': {'target_valence': 0.8, 'target_energy': 0.7},
            'sad': {'target_valence': 0.3, 'target_energy': 0.4},
            'energetic': {'target_energy': 0.9, 'target_tempo': 140},
            'calm': {'target_energy': 0.3, 'target_acousticness': 0.7},
            'upbeat': {'target_valence': 0.7, 'target_danceability': 0.7},
            'chill': {'target_energy': 0.4, 'target_valence': 0.6}
        }

        if 'mood' in filters:
            params.update(moods.get(filters['mood'], {}))

        if 'energy_level' in filters:
            # Map "high", "medium", "low" to values
            energy_map = {'high': 0.8, 'medium': 0.5, 'low': 0.3}
            params['target_energy'] = energy_map.get(filters['energy_level'], 0.5)

        if 'tempo' in filters:
            # Map "fast", "moderate", "slow" to BPM
            tempo_map = {'fast': 140, 'moderate': 110, 'slow': 80}
            params['target_tempo'] = tempo_map.get(filters['tempo'], 110)

        if 'genre' in filters:
            params['seed_genres'] = [filters['genre']]

        return params

    async def _filter_by_audio_features(
        self,
        tracks: List[Dict],
        filters: Dict
    ) -> List[Dict]:
        """Filter tracks by audio features"""

        filtered = []

        for track in tracks:
            features = await self.client.get_track_audio_features(track['id'])

            # Check filters
            if 'energy' in filters:
                if abs(features['energy'] - filters['energy']) > 0.2:
                    continue

            if 'tempo' in filters:
                if abs(features['tempo'] - filters['tempo']) > 20:
                    continue

            filtered.append(track)

        return filtered
```

### 7.4 Predictive Analytics (Week 36-37)

#### Skip Prediction Model
```python
# src/spotify_mcp/intelligence/prediction.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import List, Dict

class SkipPredictionModel:
    """Predict if user will skip a track"""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False

    def train(self, listening_history: List[Dict]):
        """
        Train model on listening history

        History format:
        {
            'track_id': '...',
            'audio_features': {...},
            'context': {...},
            'skipped': True/False,
            'listen_duration': 120  # seconds
        }
        """

        # Extract features
        X = []
        y = []

        for entry in listening_history:
            features = self._extract_features(entry)
            X.append(features)
            y.append(1 if entry['skipped'] else 0)

        X = np.array(X)
        y = np.array(y)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2%}")

        self.is_trained = True

    def predict_skip(self, track: Dict, context: Dict) -> float:
        """
        Predict probability user will skip this track

        Returns: probability (0.0 to 1.0)
        """

        if not self.is_trained:
            return 0.5  # No prediction without training

        features = self._extract_features({
            'audio_features': track.get('audio_features', {}),
            'context': context
        })

        prob = self.model.predict_proba([features])[0][1]

        return prob

    def _extract_features(self, entry: Dict) -> np.ndarray:
        """Extract feature vector from entry"""

        af = entry.get('audio_features', {})
        ctx = entry.get('context', {})

        features = [
            af.get('danceability', 0.5),
            af.get('energy', 0.5),
            af.get('valence', 0.5),
            af.get('tempo', 120) / 200,  # Normalize
            af.get('acousticness', 0.5),
            af.get('instrumentalness', 0.5),
            af.get('loudness', -10) / -60,  # Normalize
            ctx.get('hour_of_day', 12) / 24,  # Time context
            1 if ctx.get('is_weekend') else 0,
            ctx.get('playlist_position', 0) / 100,  # Position in queue
        ]

        return np.array(features)

class ListeningPatternAnalyzer:
    """Analyze user listening patterns"""

    def __init__(self, playback_history: List[Dict]):
        self.history = playback_history

    def get_peak_listening_times(self) -> List[int]:
        """Get hours when user listens most"""

        hourly_counts = [0] * 24

        for entry in self.history:
            hour = entry['played_at'].hour
            hourly_counts[hour] += 1

        # Get top 3 hours
        top_hours = sorted(
            range(24),
            key=lambda h: hourly_counts[h],
            reverse=True
        )[:3]

        return top_hours

    def get_genre_trends(self) -> Dict[str, float]:
        """Get genre listening trends over time"""

        # Group by month
        monthly_genres = {}

        for entry in self.history:
            month = entry['played_at'].strftime('%Y-%m')
            genres = entry['track'].get('genres', [])

            if month not in monthly_genres:
                monthly_genres[month] = {}

            for genre in genres:
                monthly_genres[month][genre] = monthly_genres[month].get(genre, 0) + 1

        # Calculate trends
        trends = {}
        months = sorted(monthly_genres.keys())

        for genre in set(g for m in monthly_genres.values() for g in m):
            counts = [monthly_genres[m].get(genre, 0) for m in months]

            # Simple trend: recent vs. past
            if len(counts) >= 2:
                recent = np.mean(counts[-3:])
                past = np.mean(counts[:-3])
                trend = (recent - past) / (past + 1)  # Avoid division by zero
                trends[genre] = trend

        return trends

    def predict_next_listen(self) -> Dict:
        """Predict what user will listen to next"""

        # Analyze patterns
        hour = datetime.now().hour
        day_of_week = datetime.now().weekday()

        # Get tracks listened to at similar times
        similar_context = [
            entry for entry in self.history
            if abs(entry['played_at'].hour - hour) <= 1 and
               entry['played_at'].weekday() == day_of_week
        ]

        # Find most common artists/genres
        artists = {}
        for entry in similar_context:
            artist = entry['track']['artists'][0]['name']
            artists[artist] = artists.get(artist, 0) + 1

        top_artist = max(artists.items(), key=lambda x: x[1])[0] if artists else None

        return {
            'predicted_artist': top_artist,
            'confidence': artists.get(top_artist, 0) / len(similar_context) if similar_context else 0,
            'context': {
                'hour': hour,
                'day_of_week': day_of_week
            }
        }
```

### 7.5 Contextual Awareness (Week 38-40)

#### Context-Aware Music Selection
```python
# src/spotify_mcp/intelligence/context.py
from datetime import datetime, time
from typing import Dict, Optional
import requests

class ContextAwareSystem:
    """Make music recommendations based on context"""

    def __init__(self, spotify_client):
        self.client = spotify_client

    async def get_contextual_recommendations(
        self,
        location: Optional[tuple] = None,  # (lat, lon)
        calendar_events: Optional[List[Dict]] = None
    ) -> Dict:
        """Get recommendations based on current context"""

        context = await self._gather_context(location, calendar_events)

        # Select music based on context
        recommendations = await self._select_music_for_context(context)

        return {
            'context': context,
            'recommendations': recommendations,
            'explanation': self._explain_recommendations(context)
        }

    async def _gather_context(
        self,
        location: Optional[tuple],
        calendar_events: Optional[List[Dict]]
    ) -> Dict:
        """Gather contextual information"""

        context = {
            'time': {
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'is_weekend': datetime.now().weekday() >= 5,
                'part_of_day': self._get_part_of_day()
            }
        }

        # Weather
        if location:
            weather = await self._get_weather(location)
            context['weather'] = weather

        # Calendar
        if calendar_events:
            context['calendar'] = self._analyze_calendar(calendar_events)

        # Activity detection (placeholder - would use phone sensors)
        context['activity'] = self._detect_activity()

        return context

    def _get_part_of_day(self) -> str:
        """Determine part of day"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    async def _get_weather(self, location: tuple) -> Dict:
        """Get weather from API"""
        # Use OpenWeatherMap or similar
        lat, lon = location

        # Placeholder
        return {
            'condition': 'sunny',
            'temperature': 72,
            'is_rainy': False
        }

    def _analyze_calendar(self, events: List[Dict]) -> Dict:
        """Analyze upcoming calendar events"""

        now = datetime.now()
        upcoming = [
            e for e in events
            if e['start'] > now and e['start'] < now + timedelta(hours=2)
        ]

        if not upcoming:
            return {'has_upcoming': False}

        next_event = upcoming[0]

        # Classify event type
        event_type = self._classify_event(next_event['summary'])

        return {
            'has_upcoming': True,
            'type': event_type,
            'starts_in_minutes': (next_event['start'] - now).seconds // 60
        }

    def _classify_event(self, summary: str) -> str:
        """Classify calendar event type"""

        summary_lower = summary.lower()

        if any(word in summary_lower for word in ['meeting', 'call', 'sync']):
            return 'meeting'
        elif any(word in summary_lower for word in ['workout', 'gym', 'run']):
            return 'workout'
        elif any(word in summary_lower for word in ['dinner', 'lunch', 'coffee']):
            return 'social'
        else:
            return 'other'

    def _detect_activity(self) -> str:
        """Detect current activity (placeholder)"""

        # In real implementation, use phone sensors:
        # - Accelerometer for movement
        # - GPS for location/speed
        # - Time patterns

        hour = datetime.now().hour

        if 6 <= hour < 9:
            return 'commuting'
        elif 9 <= hour < 17:
            return 'working'
        elif 17 <= hour < 19:
            return 'commuting'
        elif 19 <= hour < 22:
            return 'relaxing'
        else:
            return 'sleeping'

    async def _select_music_for_context(self, context: Dict) -> List[Dict]:
        """Select music based on context"""

        params = {}

        # Time-based
        part_of_day = context['time']['part_of_day']
        if part_of_day == 'morning':
            params.update({'target_energy': 0.6, 'target_valence': 0.7})
        elif part_of_day == 'night':
            params.update({'target_energy': 0.3, 'target_acousticness': 0.7})

        # Weather-based
        if 'weather' in context:
            if context['weather']['is_rainy']:
                params.update({'target_acousticness': 0.6, 'target_valence': 0.4})
            elif context['weather']['condition'] == 'sunny':
                params.update({'target_valence': 0.8})

        # Calendar-based
        if 'calendar' in context and context['calendar']['has_upcoming']:
            event_type = context['calendar']['type']

            if event_type == 'meeting':
                # Focus music before meetings
                params.update({'target_instrumentalness': 0.7, 'target_energy': 0.5})
            elif event_type == 'workout':
                params.update({'target_energy': 0.9, 'target_tempo': 140})

        # Activity-based
        activity = context.get('activity')
        if activity == 'working':
            params.update({'target_instrumentalness': 0.6})
        elif activity == 'commuting':
            params.update({'target_energy': 0.6})

        # Get recommendations
        recommendations = await self.client.get_recommendations(
            limit=30,
            **params
        )

        return recommendations['tracks']

    def _explain_recommendations(self, context: Dict) -> str:
        """Generate human-readable explanation"""

        explanations = []

        if context['time']['part_of_day'] == 'morning':
            explanations.append("energizing morning music")
        elif context['time']['part_of_day'] == 'night':
            explanations.append("calming evening music")

        if 'weather' in context:
            if context['weather']['is_rainy']:
                explanations.append("cozy rainy day vibes")

        if 'calendar' in context and context['calendar']['has_upcoming']:
            event_type = context['calendar']['type']
            if event_type == 'meeting':
                explanations.append("focus music before your meeting")

        return "Selected " + " with ".join(explanations) if explanations else "Personalized recommendations"
```

---

## 📊 PHASE 8: Analytics & Insights (Weeks 41-48)

**Goal:** Comprehensive analytics dashboard and insights
**Dependencies:** Phase 1 (database), Phase 7 (ML features)
**Deliverables:** Analytics engine, visualization dashboard

### 8.1 Analytics Data Collection (Week 41-42)

#### Event Tracking System
```python
# src/spotify_mcp/analytics/events.py
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

class AnalyticsEventTracker:
    """Track user interactions and listening events"""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def track_play_event(
        self,
        user_id: str,
        track: Dict,
        context: Optional[Dict] = None
    ):
        """Track when a track is played"""

        event = PlaybackEvent(
            user_id=user_id,
            track_id=track['id'],
            track_name=track['name'],
            artist_name=track['artists'][0]['name'],
            album_name=track['album']['name'],
            duration_ms=track['duration_ms'],
            context_type=context.get('type') if context else None,
            context_uri=context.get('uri') if context else None,
            played_at=datetime.utcnow()
        )

        self.db.add(event)
        await self.db.commit()

    async def track_skip_event(
        self,
        user_id: str,
        track_id: str,
        position_ms: int,
        reason: Optional[str] = None
    ):
        """Track when a track is skipped"""

        event = SkipEvent(
            user_id=user_id,
            track_id=track_id,
            position_ms=position_ms,
            skip_percentage=(position_ms / track['duration_ms'] * 100),
            reason=reason,
            skipped_at=datetime.utcnow()
        )

        self.db.add(event)
        await self.db.commit()

    async def track_search_event(
        self,
        user_id: str,
        query: str,
        search_type: str,
        results_count: int
    ):
        """Track search queries"""

        event = SearchEvent(
            user_id=user_id,
            query=query,
            search_type=search_type,
            results_count=results_count,
            searched_at=datetime.utcnow()
        )

        self.db.add(event)
        await self.db.commit()
```

### 8.2 Analytics Computation Engine (Week 43-45)

#### Analytics Calculator
```python
# src/spotify_mcp/analytics/calculator.py
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func
from collections import defaultdict

class AnalyticsCalculator:
    """Calculate analytics metrics"""

    def __init__(self, db_session: Session, user_id: str):
        self.db = db_session
        self.user_id = user_id

    async def calculate_listening_stats(
        self,
        period: str = 'month'  # day, week, month, year, all_time
    ) -> Dict:
        """Calculate comprehensive listening statistics"""

        start_date = self._get_start_date(period)

        # Total listening time
        total_time = await self._calculate_total_listening_time(start_date)

        # Top tracks
        top_tracks = await self._get_top_tracks(start_date, limit=50)

        # Top artists
        top_artists = await self._get_top_artists(start_date, limit=50)

        # Top genres
        top_genres = await self._get_top_genres(start_date)

        # Listening patterns
        hourly_distribution = await self._get_hourly_distribution(start_date)
        daily_distribution = await self._get_daily_distribution(start_date)

        # Discovery metrics
        discovery = await self._calculate_discovery_metrics(start_date)

        # Audio feature averages
        audio_features = await self._calculate_audio_feature_averages(start_date)

        return {
            'period': period,
            'total_listening_time_hours': total_time / 3600,
            'total_tracks_played': await self._count_tracks_played(start_date),
            'unique_tracks': await self._count_unique_tracks(start_date),
            'unique_artists': await self._count_unique_artists(start_date),
            'top_tracks': top_tracks,
            'top_artists': top_artists,
            'top_genres': top_genres,
            'hourly_distribution': hourly_distribution,
            'daily_distribution': daily_distribution,
            'discovery': discovery,
            'audio_features': audio_features
        }

    async def _calculate_total_listening_time(self, start_date: datetime) -> int:
        """Calculate total listening time in seconds"""

        result = self.db.query(
            func.sum(PlaybackEvent.duration_ms) / 1000
        ).filter(
            PlaybackEvent.user_id == self.user_id,
            PlaybackEvent.played_at >= start_date
        ).scalar()

        return int(result or 0)

    async def _get_top_tracks(self, start_date: datetime, limit: int) -> List[Dict]:
        """Get most played tracks"""

        results = self.db.query(
            PlaybackEvent.track_id,
            PlaybackEvent.track_name,
            PlaybackEvent.artist_name,
            func.count().label('play_count')
        ).filter(
            PlaybackEvent.user_id == self.user_id,
            PlaybackEvent.played_at >= start_date
        ).group_by(
            PlaybackEvent.track_id,
            PlaybackEvent.track_name,
            PlaybackEvent.artist_name
        ).order_by(
            func.count().desc()
        ).limit(limit).all()

        return [
            {
                'track_id': r.track_id,
                'name': r.track_name,
                'artist': r.artist_name,
                'play_count': r.play_count
            }
            for r in results
        ]

    async def _get_hourly_distribution(self, start_date: datetime) -> Dict[int, int]:
        """Get play count distribution by hour of day"""

        results = self.db.query(
            func.extract('hour', PlaybackEvent.played_at).label('hour'),
            func.count().label('count')
        ).filter(
            PlaybackEvent.user_id == self.user_id,
            PlaybackEvent.played_at >= start_date
        ).group_by('hour').all()

        distribution = {i: 0 for i in range(24)}
        for r in results:
            distribution[int(r.hour)] = r.count

        return distribution

    async def _calculate_discovery_metrics(self, start_date: datetime) -> Dict:
        """Calculate discovery-related metrics"""

        # New artists discovered
        all_time_artists = set(
            self.db.query(PlaybackEvent.artist_name).filter(
                PlaybackEvent.user_id == self.user_id,
                PlaybackEvent.played_at < start_date
            ).distinct()
        )

        period_artists = set(
            self.db.query(PlaybackEvent.artist_name).filter(
                PlaybackEvent.user_id == self.user_id,
                PlaybackEvent.played_at >= start_date
            ).distinct()
        )

        new_artists = period_artists - all_time_artists

        # Similar for tracks
        # ...

        return {
            'new_artists_discovered': len(new_artists),
            'discovery_rate': len(new_artists) / len(period_artists) if period_artists else 0,
        }

    def _get_start_date(self, period: str) -> datetime:
        """Get start date for period"""

        now = datetime.utcnow()

        if period == 'day':
            return now - timedelta(days=1)
        elif period == 'week':
            return now - timedelta(weeks=1)
        elif period == 'month':
            return now - timedelta(days=30)
        elif period == 'year':
            return now - timedelta(days=365)
        else:  # all_time
            return datetime(2000, 1, 1)
```

### 8.3 Visualization Dashboard (Week 46-47)

#### React Dashboard
```typescript
// analytics-dashboard/src/components/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface AnalyticsData {
  period: string;
  total_listening_time_hours: number;
  top_tracks: Array<{name: string; artist: string; play_count: number}>;
  hourly_distribution: {[hour: number]: number};
  audio_features: {[feature: string]: number};
}

export function AnalyticsDashboard() {
  const [period, setPeriod] = useState('month');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics(period);
  }, [period]);

  const fetchAnalytics = async (period: string) => {
    setLoading(true);
    const response = await fetch(`/api/analytics?period=${period}`);
    const analyticsData = await response.json();
    setData(analyticsData);
    setLoading(false);
  };

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="dashboard">
      <header>
        <h1>Your Music Analytics</h1>
        <select value={period} onChange={e => setPeriod(e.target.value)}>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
          <option value="all_time">All Time</option>
        </select>
      </header>

      {/* Summary Cards */}
      <div className="summary-cards">
        <Card
          title="Listening Time"
          value={`${data.total_listening_time_hours.toFixed(1)} hrs`}
          icon="🎵"
        />
        <Card
          title="Tracks Played"
          value={data.total_tracks_played}
          icon="🎧"
        />
        <Card
          title="New Artists"
          value={data.discovery.new_artists_discovered}
          icon="✨"
        />
        <Card
          title="Unique Tracks"
          value={data.unique_tracks}
          icon="📀"
        />
      </div>

      {/* Top Tracks */}
      <section className="top-tracks">
        <h2>Top Tracks</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.top_tracks.slice(0, 10)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="play_count" fill="#1db954" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Listening Patterns */}
      <section className="listening-patterns">
        <h2>Listening Patterns</h2>
        <h3>By Hour of Day</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={formatHourlyData(data.hourly_distribution)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="plays" stroke="#1db954" />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Audio Features */}
      <section className="audio-features">
        <h2>Your Music DNA</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={formatAudioFeatures(data.audio_features)}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#1db954"
              label
            />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </section>

      {/* Genre Distribution */}
      <section className="genres">
        <h2>Top Genres</h2>
        <div className="genre-tags">
          {data.top_genres.map((genre, i) => (
            <GenreTag key={i} genre={genre} rank={i + 1} />
          ))}
        </div>
      </section>
    </div>
  );
}

function Card({ title, value, icon }: {title: string, value: any, icon: string}) {
  return (
    <div className="card">
      <div className="icon">{icon}</div>
      <div className="content">
        <h3>{title}</h3>
        <p className="value">{value}</p>
      </div>
    </div>
  );
}

function formatHourlyData(hourlyDist: {[hour: number]: number}) {
  return Object.entries(hourlyDist).map(([hour, plays]) => ({
    hour: `${hour}:00`,
    plays
  }));
}

function formatAudioFeatures(features: {[key: string]: number}) {
  return Object.entries(features).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value * 100
  }));
}
```

### 8.4 Automated Insights Generation (Week 48)

#### Insight Engine
```python
# src/spotify_mcp/analytics/insights.py
from typing import List, Dict
from datetime import datetime, timedelta

class InsightGenerator:
    """Generate automated insights from analytics data"""

    def __init__(self, analytics_calculator: AnalyticsCalculator):
        self.calculator = analytics_calculator

    async def generate_weekly_insights(self, user_id: str) -> List[Dict]:
        """Generate weekly insights"""

        # Get data for this week and last week
        this_week = await self.calculator.calculate_listening_stats('week')
        last_week = await self.calculator.calculate_listening_stats_for_range(
            datetime.utcnow() - timedelta(weeks=2),
            datetime.utcnow() - timedelta(weeks=1)
        )

        insights = []

        # Listening time comparison
        time_change = (
            (this_week['total_listening_time_hours'] -
             last_week['total_listening_time_hours']) /
            last_week['total_listening_time_hours'] * 100
        )

        if abs(time_change) > 20:
            insights.append({
                'type': 'listening_time_change',
                'title': f"You listened {'more' if time_change > 0 else 'less'} this week!",
                'description': f"Your listening time {'increased' if time_change > 0 else 'decreased'} by {abs(time_change):.0f}%",
                'icon': '📈' if time_change > 0 else '📉'
            })

        # New discovery
        if this_week['discovery']['new_artists_discovered'] > 5:
            insights.append({
                'type': 'discovery',
                'title': "You're exploring new music!",
                'description': f"You discovered {this_week['discovery']['new_artists_discovered']} new artists this week",
                'icon': '✨'
            })

        # Mood shift
        this_valence = this_week['audio_features']['valence']
        last_valence = last_week['audio_features']['valence']

        if this_valence - last_valence > 0.2:
            insights.append({
                'type': 'mood',
                'title': "Your music got happier!",
                'description': "You've been listening to more upbeat tracks this week",
                'icon': '😊'
            })
        elif last_valence - this_valence > 0.2:
            insights.append({
                'type': 'mood',
                'title': "Your music got mellower",
                'description': "You've been listening to calmer tracks this week",
                'icon': '😌'
            })

        # Obsession detection
        top_track = this_week['top_tracks'][0]
        if top_track['play_count'] > 20:
            insights.append({
                'type': 'obsession',
                'title': "You've been obsessed!",
                'description': f"You played '{top_track['name']}' {top_track['play_count']} times",
                'icon': '🔥',
                'track': top_track
            })

        # Listening pattern insights
        peak_hour = max(
            this_week['hourly_distribution'].items(),
            key=lambda x: x[1]
        )[0]

        if this_week['hourly_distribution'][peak_hour] > 50:
            time_label = self._get_time_label(peak_hour)
            insights.append({
                'type': 'pattern',
                'title': f"You're a {time_label} listener",
                'description': f"Most of your listening happens around {peak_hour}:00",
                'icon': '🕐'
            })

        return insights

    def _get_time_label(self, hour: int) -> str:
        """Get label for hour"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    async def generate_year_in_review(self, user_id: str, year: int) -> Dict:
        """Generate Spotify Wrapped-style year in review"""

        # Get full year data
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        stats = await self.calculator.calculate_listening_stats_for_range(
            start_date, end_date
        )

        # Calculate special stats
        top_month = await self._get_top_listening_month(user_id, year)
        longest_streak = await self._calculate_longest_streak(user_id, year)
        total_genres = len(stats['top_genres'])

        # Create narrative
        minutes = int(stats['total_listening_time_hours'] * 60)

        return {
            'year': year,
            'total_minutes': minutes,
            'total_hours': stats['total_listening_time_hours'],
            'top_tracks': stats['top_tracks'][:5],
            'top_artists': stats['top_artists'][:5],
            'top_genres': stats['top_genres'][:5],
            'total_genres_explored': total_genres,
            'top_month': top_month,
            'longest_streak_days': longest_streak,
            'unique_tracks': stats['unique_tracks'],
            'audio_personality': self._describe_audio_personality(stats['audio_features']),
            'fun_facts': [
                f"You listened to {minutes:,} minutes of music",
                f"That's {minutes/60/24:.1f} days of pure music",
                f"You explored {total_genres} different genres",
                f"Your longest listening streak was {longest_streak} days"
            ]
        }

    def _describe_audio_personality(self, features: Dict) -> str:
        """Describe listening personality based on audio features"""

        if features['energy'] > 0.7 and features['danceability'] > 0.7:
            return "The Party Starter"
        elif features['valence'] > 0.7:
            return "The Optimist"
        elif features['acousticness'] > 0.6:
            return "The Acoustic Soul"
        elif features['instrumentalness'] > 0.5:
            return "The Deep Thinker"
        elif features['energy'] < 0.4:
            return "The Chill Vibe"
        else:
            return "The Eclectic Explorer"
```

---

**Due to length constraints, shall I continue with the remaining phases (9-15) in a final part?**

The remaining phases are:
- Phase 9: Automation & Workflows
- Phase 10: Enterprise Features
- Phase 11: Cloud & Deployment
- Phase 12: Real-Time & WebSocket
- Phase 13: Plugin Architecture
- Phase 14: Advanced Features
- Phase 15: Launch & Scale

Should I:
1. ✅ Complete all remaining phases
2. ✅ Create an executive summary + implementation timeline
3. ✅ Start implementing Phase 1 immediately

Your choice!

"""
Test script for audio features API endpoint
"""
from pathlib import Path
import sys

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.tools.tracks import get_tracks_audio_features

def test_audio_features():
    """Test audio features with known-good track IDs"""
    
    # Get authenticated client
    print("Getting authenticated Spotify client...")
    client = get_spotify_client()
    
    # Test with a very popular track that should definitely exist
    # Using "Blinding Lights" by The Weeknd - one of most streamed songs
    known_good_id = "0VjIjW4GlUZAMYd2vXMi3b"  # Blinding Lights
    
    print(f"\nTesting with known-good track ID: {known_good_id}")
    print("Track: Blinding Lights by The Weeknd")
    print("-" * 60)
    
    try:
        result = get_tracks_audio_features(client, [known_good_id])
        print("✅ SUCCESS!")
        print("\nAudio Features:")
        if result and len(result) > 0:
            features = result[0]
            if features:
                print(f"  Tempo: {features.get('tempo', 'N/A')} BPM")
                print(f"  Energy: {features.get('energy', 'N/A')}")
                print(f"  Danceability: {features.get('danceability', 'N/A')}")
                print(f"  Valence: {features.get('valence', 'N/A')}")
                print(f"  Key: {features.get('key', 'N/A')}")
                print(f"  Mode: {features.get('mode', 'N/A')}")
            else:
                print("  ⚠️ No audio features available for this track")
        else:
            print("  ⚠️ Empty result returned")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nThis indicates the issue is not with the specific track ID you provided.")
        return
    
    # Now test with the track ID from your screenshot
    print("\n" + "=" * 60)
    your_track_id = "5ozqshq2dtU7SYCpCBuONE"
    print(f"\nTesting with your track ID: {your_track_id}")
    print("-" * 60)
    
    try:
        result = get_tracks_audio_features(client, [your_track_id])
        print("✅ SUCCESS!")
        print("\nAudio Features:")
        if result and len(result) > 0:
            features = result[0]
            if features:
                print(f"  Tempo: {features.get('tempo', 'N/A')} BPM")
                print(f"  Energy: {features.get('energy', 'N/A')}")
                print(f"  Danceability: {features.get('danceability', 'N/A')}")
                print(f"  Valence: {features.get('valence', 'N/A')}")
            else:
                print("  ⚠️ No audio features available for this track")
                print("  This could mean:")
                print("    - Track is unavailable in your region")
                print("    - Track has been removed from Spotify")
                print("    - Track is too new and features haven't been calculated")
        else:
            print("  ⚠️ Empty result returned")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nPossible causes:")
        print("  - Track is region-locked or unavailable")
        print("  - Track has been removed from Spotify")
        print("  - Invalid track ID format")

if __name__ == "__main__":
    test_audio_features()

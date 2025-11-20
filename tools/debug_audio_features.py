"""Debug audio features API endpoint"""
from pathlib import Path
import sys

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from spotify_mcp.auth import get_spotify_client

def debug_audio_features():
    print("Getting Spotify client...")
    sp = get_spotify_client()  # Returns spotipy.Spotify directly
    
    print(f"Authenticated as: {sp.me()['display_name']}")
    
    test_id = "0VjIjW4GlUZAMYd2vXMi3b"  # Blinding Lights
    
    # Test 1: Can we get track info?
    print(f"\nTest 1: Getting track info for {test_id}")
    try:
        track = sp.track(test_id)
        print(f"✅ Track: {track['name']} by {track['artists'][0]['name']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Can we get audio features?
    print(f"\nTest 2: Getting audio features")
    try:
        features = sp.audio_features(tracks=[test_id])
        print(f"✅ Raw result type: {type(features)}")
        print(f"✅ Result length: {len(features) if features else 0}")
        if features and features[0]:
            print(f"✅ Tempo: {features[0].get('tempo')} BPM")
            print(f"✅ Energy: {features[0].get('energy')}")
        else:
            print("⚠️ Features returned None or empty")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_audio_features()

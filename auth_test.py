import sys
sys.path.insert(0, 'src')
from spotify_mcp.auth import get_spotify_client

print('Starting authentication...')
client = get_spotify_client()
user = client.current_user()
print(f'Successfully authenticated as: {user["display_name"]}')
print(f'Email: {user["email"]}')

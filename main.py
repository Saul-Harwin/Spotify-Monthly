CLIENT_ID = "a450350db6d64e75b8bde3305d7c5ff9"
CLIENT_SECRET = "40ca4a8f66304ab0abe7ac56d13523c3"
REDIRECT_URI = "http://localhost:3000"

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'

import requests

auth_code = requests.get(AUTH_URL, {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': 'https://open.spotify.com/collection/playlists',
    'scope': 'playlist-modify-private',
})
print(auth_code)

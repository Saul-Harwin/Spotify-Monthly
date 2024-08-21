# import sys
# import spotipy
# import spotipy.util as util

# USERNAME = "saulharwin"
# SCOPE = "user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private"
# CLIENT_ID = "a450350db6d64e75b8bde3305d7c5ff9"
# CLIENT_SECRET = "40ca4a8f66304ab0abe7ac56d13523c3"
# REDIRECT_URI = "http://192.168.5.236:3000/callback"

# AUTH_URL = 'https://accounts.spotify.com/authorize'
# TOKEN_URL = 'https://accounts.spotify.com/api/token'
# BASE_URL = 'https://api.spotify.com/v1/'


# if __name__ == '__main__':
#     token = util.prompt_for_user_token(USERNAME, scope = SCOPE, client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri=REDIRECT_URI)
#     if token:
#       sp = spotipy.Spotify(auth=token)
#       myTopArtists = sp.current_user_top_artists(5, 0, 'short_term')

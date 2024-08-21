import requests
import urllib.parse   
import json

from flask import Flask, redirect, request, jsonify, session
from datetime import datetime, timedelta

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'aksyfhljnCljvr84732yˆ&G*bb(*Nkmdsf&Bakjsdn1264m)'

CLIENT_ID = "a450350db6d64e75b8bde3305d7c5ff9"
CLIENT_SECRET = "40ca4a8f66304ab0abe7ac56d13523c3"
REDIRECT_URI = "http://192.168.5.236:3000/callback"

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    return "Welcome to my spotify app <a href='/login'>Login with Spotify</a>"


@app.route('/login')
def login():
    scope = "user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": False # turn this off once finished this makes them login each time even if already logged in. 
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print("Hello")
    return redirect(auth_url)
 
# Where spotify goes after login request
@app.route("/callback")
def callback():
    print("I've managed to call back")
    if "error" in request.args:
        return jsonify({"error": request.args['error']})
    
    if "code" in request.args:
        request_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

    response = requests.post(TOKEN_URL, data=request_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    session['name'] = "saulharwin"
    
    print("Successful login")

    return redirect("/top-tracks-month")

    
@app.route("/playlists")
def Get_Playlists():
    if "access_token" not in session:
        return redirect("/login")
    
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    response = requests.get(BASE_URL +  "me/playlists", headers=headers)
    playlists = response.json()

    return jsonify(playlists)

@app.route("/refresh-token")
def Refresh_Token():
    if "refresh_token" not in session:
        return redirect("/login")
    
    if datetime.now().timestamp > session["expires_at"]:
        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        } 

        response = requests.post(TOKEN_URL, data=request_body) 
        new_token_info = response.json()

        session["access_token"] = new_token_info["access_token"]
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect("/playlists")
    

@app.route("/top-tracks-month")
def Top_Tracks_Month():
    print("top tracks")
    if "refresh_token" not in session:
        return redirect("/login")
    
    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")
    
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    params = {
        "type": "tracks",
        "time_range": "short_term",
        "limit": "20",
        "offset": "0"
    }

    response = requests.get(BASE_URL +  "me/top/tracks", headers=headers, params=params)
    response = response.json()["items"]

    tracks = []
    
    for i in response:
        track = {
            "name": i["name"],
            "track_number": i["track_number"],
            "uri": i["uri"]
        }
 
        tracks.append(track)

    track_uris = []

    for track in tracks:
        track_uris.append(track["uri"])

    playlist_id, exists = Check_Playlist_Exists(f"Songs of {datetime.now().month} {datetime.now().year}")
    if not exists:
        print("Playlist didn't already exist")
        playlist_id = Create_Playlist()

    success = Populate_Playlist(playlist_id, track_uris)

    if success:
        print("Playlist creation was successful")
        return "Playist Creation was successful"

    print("Playlist creation was unsuccesful")
    return "Playlist Creation was Unsuccesful"

def Create_Playlist():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    request_body = json.dumps({
        "name": f"Songs of {datetime.now().month} {datetime.now().year}",
        "description": "This playlist is creation of Saul Harwin's monthly spotify playlist generator which gathers the users top 20 songs of the month and creates a playlists.",
        "public": True
    })

    response = requests.post(BASE_URL +  f"users/{session['name']}/playlists", data=request_body,  headers=headers)
    response = response.json()

    playlist_id = response["id"]
    return playlist_id  

def Populate_Playlist(playlist_id, track_uris):
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    request_body = json.dumps({
        "uris": track_uris
    })

    response = requests.post(BASE_URL +  f"playlists/{playlist_id}/tracks", data=request_body,  headers=headers)
    response = response.json()

    if "snapshot_id" in response:
        return True
    
    return False
    
def Check_Playlist_Exists(playlist_name):
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    params = {
        "limit": 50
    }


    response = requests.get(BASE_URL +  f"users/{session['name']}/playlists", headers=headers)
    response = response.json()["items"]

    for playlist in response:
        if playlist["name"] == playlist_name:
            playlist_id = playlist["id"]
            return playlist_id, True

    return "null", False


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="cron", minute=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3000", debug=True)

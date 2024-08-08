import requests
import urllib.parse   


from flask import Flask, redirect, request, jsonify, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'aksyfhljnCljvr84732yˆ&G*bb(*Nkmdsf&Bakjsdn1264m)'

CLIENT_ID = "a450350db6d64e75b8bde3305d7c5ff9"
CLIENT_SECRET = "40ca4a8f66304ab0abe7ac56d13523c3"
REDIRECT_URI = "http://localhost:3000/callback"

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    return "Welcome to my spotify app <a href='/login'>Login with Spotify</a>"


@app.route('/login')
def login():
    scope = "user-read-private user-read-email"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": True # turn this off once finished this makes them login each time even if already logged in. 
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)
 
# Where spotify goes after login request
@app.route("/callback")
def callback():
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

    return redirect("/playlists")

    
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

app.route("/refresh-token")
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
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3000", debug=True)
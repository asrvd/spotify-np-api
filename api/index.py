import requests
from flask import Flask, jsonify, Response, make_response, request
from dotenv import load_dotenv, find_dotenv
from os import getenv
import json

load_dotenv(find_dotenv())

def get_token():
    '''Get a new access token'''
    r = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': getenv('REFRESH_TOKEN'),
        'client_id': getenv('CLIENT_ID'),
        'client_secret': getenv('CLIENT_SECRET'),
    })
    try:
        return r.json()['access_token']
    except BaseException:
        raise Exception(r.json())


def spotify_request(endpoint):
    '''Make a request to the specified endpoint'''
    r = requests.get(
        f'https://api.spotify.com/v1/{endpoint}',
        headers={'Authorization': f'Bearer {get_token()}'}
    )
    return {} if r.status_code == 204 else r.json()

def get_np():
    data = spotify_request('me/player/currently-playing')
    if data:
        item = data['item']
    else:
        item = spotify_request('me/player/recently-played?limit=3')['items'][0]['track']
    return {
        'artist': item['artists'][0]['name'].replace('&', '&amp;'),
        'song': item['name'].replace('&', '&amp;'),
        'url' : item['external_urls']['spotify'].replace('&', '&amp;'),
    }

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    res = make_response(jsonify(get_np()), 200)
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Credentials"] : true
    return res

if __name__ == '__main__':
    app.run(debug=True)

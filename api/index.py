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

def get_all_top():
    dt = spotify_request('me/top/tracks?limit=20&time_range=short_term')
    top_list = []
    if dt:
        items = dt['items']
    for item in items:
        dict = {
            'artist': item['artists'][0]['name'].replace('&', '&amp;'),
            'song': item['name'].replace('&', '&amp;'),
            'url': item['external_urls']['spotify'],
            'image': item['album']['external_urls']['images'][1]['url']
        }
        top_list.append(dict)
    return top_list.reverse()

def get_np():
    data1 = spotify_request('me/player/currently-playing')
    data2 = spotify_request('me/top/tracks?limit=1&time_range=short_term')
    if data1:
        item = data1['item']
    else:
        item = spotify_request('me/player/recently-played?limit=3')['items'][0]['track']
    return {
        'np': {
            'artist': item['artists'][0]['name'].replace('&', '&amp;'),
            'song': item['name'].replace('&', '&amp;'),
            'url' : item['external_urls']['spotify'],
        },
        'top': {
            'artist': data2['items'][0]['artists'][0]['name'].replace('&', '&amp;'),
            'song': data2['items'][0]['name'].replace('&', '&amp;'),
            'url' : data2['items'][0]['external_urls']['spotify'],
        },
        'all-top': get_all_top()
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

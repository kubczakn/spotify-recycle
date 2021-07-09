import time
import json
import spotipy
import config
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    scope=scope,
                    client_id=config.SPOTIPY_CLIENT_ID,
                    client_secret=config.SPOTIPY_CLIENT_SECRET,
                    redirect_uri=config.SPOTIPY_REDIRECT_URI))


def get_user_playlists():
    playlists = sp.current_user_playlists()
    res = {playlist['name']: playlist['id'] for playlist in playlists['items']}
    if 'Recycle Bin' not in res.keys():
        user_id = sp.me()['id']
        sp.user_playlist_create(user_id, name='Recycle Bin')
        res = get_user_playlists()
    return res


def get_playlist_tracks(playlists):
    res = {}
    for playlist in playlists.keys():
        res[playlist] = []
        tracks = sp.playlist_items(playlists[playlist])
        for track in tracks['items']:
            res[playlist].append([track['track']['name'], track['track']['id']])
    return res


def check_playlists(old_playlists, playlist_ids, path):
    new_playlists = get_playlist_tracks(playlist_ids)
    for playlist in new_playlists.keys():
        if playlist in old_playlists.keys() and playlist != 'Recycle Bin':
            for track in old_playlists[playlist]:
                if track not in new_playlists[playlist]:
                    sp.playlist_add_items(playlist_ids['Recycle Bin'], [track[1]])
    with open(path, '+w') as f:
        f.write(json.dumps(new_playlists))
    return


# TODO: New Workflow
#       1. User authenticates, add current playlists to records
#       2. User decides to "recycle" anything they've deleted
#       3. Script runs and adds anything removed to recycle bin, updates records

def recycle():
    playlist_ids = get_user_playlists()
    path = 'data.json'
    with open(path) as f:
        playlist_tracks = json.load(f)
    check_playlists(playlist_tracks, playlist_ids, path)


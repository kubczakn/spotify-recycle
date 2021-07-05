import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def get_user_playlists():
    res = {}
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        res[playlist['name']] = playlist['id']
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


def check_playlists(old_playlists, playlist_ids):
    new_playlists = get_playlist_tracks(playlist_ids)
    for playlist in new_playlists.keys():
        if playlist in old_playlists.keys():
            for track in old_playlists[playlist]:
                if track not in new_playlists[playlist]:
                    sp.playlist_add_items('Recycle Bin', track[1])
    return


def main():
    playlist_ids = get_user_playlists()
    # playlist_tracks = get_playlist_tracks(playlist_ids)
    path = 'data.json'
    # with open(path, '+w') as f:
    #     f.write(json.dumps(playlist_tracks))
    with open(path) as f:
        playlist_tracks = json.load(f)
    print(playlist_tracks)


if __name__ == '__main__':
    main()

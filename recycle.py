import sqlite3
from sqlite3 import Error
import json
import spotipy
import config
from spotipy.oauth2 import SpotifyOAuth

conn = sqlite3.connect('sql/tracks.db')
scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET,
    redirect_uri=config.SPOTIPY_REDIRECT_URI))


def query_db(table):
    cursor = conn.execute(
        '''SELECT * FROM %s;''' % table
    )
    res = {}
    rows = cursor.fetchall()
    if not rows:
        res, recycle_bin_id = get_playlists()

    else:
        for row in rows:
            playlist_id = row[1]
            track_id = row[2]
            if playlist_id not in res.keys():
                res[playlist_id] = []
            res[playlist_id].append(track_id)
    return res


def insert_db(playlists, table):
    conn.execute(
        '''DELETE FROM %s''' % table
    )
    conn.commit()
    for playlist_id in playlists.keys():
        for track_id in playlists[playlist_id]:
            conn.execute(
                '''INSERT INTO %s (PLAYLIST_ID, TRACK_ID)
                    VALUES(?, ?);''' % table, (playlist_id, track_id)
            )
    conn.commit()


def get_playlists():
    playlists = sp.current_user_playlists()
    res = {}
    recycle_bin_id = ''
    for playlist in playlists['items']:
        playlist_id = playlist['id']
        tracks = sp.playlist_items(playlist_id)
        res[playlist_id] = []
        if playlist['name'] == 'Recycle Bin':
            recycle_bin_id = playlist_id
        for track in tracks['items']:
            res[playlist_id].append(track['track']['id'])
    if recycle_bin_id == '':
        user_id = sp.me()['id']
        sp.user_playlist_create(user_id, name='Recycle Bin')
    return res, recycle_bin_id


def check_playlists(table):
    new_playlists, recycle_bin_id = get_playlists()
    old_playlists = query_db(table)
    for playlist in new_playlists.keys():
        if playlist in old_playlists.keys() and playlist != 'Recycle Bin':
            for track in old_playlists[playlist]:
                if track not in new_playlists[playlist]:
                    sp.playlist_add_items(recycle_bin_id, [track])
    insert_db(new_playlists, table)
    return


def recycle():
    curr_user = sp.current_user()['display_name']
    table_name = curr_user + '_tracks'
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS %s 
        (ID INTEGER  PRIMARY KEY AUTOINCREMENT,
        PLAYLIST_ID TEXT NOT NULL, 
        TRACK_ID TEXT NOT NULL);''' % table_name)
    check_playlists(table_name)

    # TODO: Select from user table, create data structure, compare with current


if __name__ == '__main__':
    recycle()

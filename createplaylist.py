import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

from exceptions import ResponseException
from secrets import spotify_token, spotify_user_id




class CreatePlaylist:
    def __init__(self):
        pass
    def get_youtube_client(self):
        pass
    def get_liked_videos(self):
        pass
    def create_playlist(self):
        pass
    def get_spotify_url(self):
        pass
    def add_song_to_playlist(self):
        pass

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
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}
    
    def get_youtube_client(self):
        """Log into YouTube, copied from YouTube Data API"""
        # Disable OAuthlib's HTTPS verification when running locally. DO NOT leave enabled in production
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "YouTube"
        api_version = "v3"
        client_secrets_file = "clientsecret.json"

        # Pull credentials from API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # YouTube Data API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client


    def get_liked_videos(self):
        """Find liked videos and create a dictionary of important song information"""
        request = self.youtube_client.videos().list(
            part = "snippet, contentDetails, statistics",
            myRating = "like"
        )
        response = request.execute()
        
    def create_playlist(self):
        pass
    def get_spotify_url(self):
        pass
    def add_song_to_playlist(self):
        pass

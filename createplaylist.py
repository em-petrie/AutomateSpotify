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
        """Find liked videos and create a dictionary of the important song information"""
        request = self.youtube_client.videos().list(
            part = "snippet, contentDetails, statistics",
            myRating = "like"
        )
        response = request.execute()

        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"]
            )
            video = youtube_dl.YouTubeDL({}).extract_info(
                youtube_url, download = False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    "spotify_uri": self.get_spotify_uri(song_name, artist)
                }

    def create_playlist(self):
        """Add a new playlist"""
        request_body = json.dumps({
            "name": "YouTube Liked Videos",
            "description": "All liked YouTube videos",
            "public": True
        })
        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorisation": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        return response_json["id"]

    def get_spotify_uri(self, song_name, artist):
        """Search for songs"""
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorisation": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        return uri

    def add_song_to_playlist(self):
        """Add songs from liked videos to the new Spotify playlist"""

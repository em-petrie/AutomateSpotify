import json
import os

import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

import toml
import base64 
# from pprint import pprint
from exceptions import ResponseException
from secrets import spotify_token, spotify_user_id

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.oauth2 import  SpotifyPKCE, SpotifyImplicitGrant


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
            api_service_name, api_version, credentials = credentials)

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
            # error opening this url when running ??
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])
            
            video = youtube_dl.YoutubeDL({}).extract_info(
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
        """Create a new Spotify playlist"""
        request_body = json.dumps({
            "name": "Liked from YouTube",
            "description": "All liked YouTube videos",
            "public": True
        })
        # update uri
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.spotify_user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorisation": "Bearer {}".format(spotify_token) 
            }
        )
        response_json = response.json()
        # should return playlist ID for add_song_to_playlist
        return response_json["id"]

    def get_spotify_uri(self, song_name, artist):
        """Search for song"""
        # update uri
        query = "https://api.spotify.com/v1/search?type=track%2C%20artist&limit=20&offset=0".format(
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

        # return first song from search results
        uri = songs[0]["uri"]

        return uri

    def add_song_to_playlist(self):
        """Add songs from liked videos to the new Spotify playlist"""
        self.get_liked_videos()
        uris = [info["spotify_uri"]
            for song, info in self.all_song_info.items()]

        playlist_id = self.create_playlist()

        request_data = json.dumps(uris)
        # update uri
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data = request_data,
            headers = {
                "Content-Type": "application/json",
                "Authorisation": "Bearer {}".format(spotify_token)
            }
        )
        # check response 
        if response.status_code != 200:
            raise ResponseException(response.status_code)
        response_json = response.json()
        return response_json

if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()


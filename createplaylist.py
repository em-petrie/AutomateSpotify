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
        
        # self._spotify_dict = spotifyDict
        # self._spotify_cid =  self._spotify_dict["oauth2Providers"]["spotify"]["clientId"]
        # self._spotify_csecret = self._spotify_dict["oauth2Providers"]["spotify"]["clientSecret"]
        # spotify_creds = SpotifyClientCredentials(client_id=self._spotify_cid, client_secret=self._spotify_csecret)
        # self._redirect_uri =self._spotify_dict["oauth2Providers"]["spotify"]["redirectURL"]
        # scope = 'playlist-modify-public'
        # implicit = SpotifyImplicitGrant(client_id=self._spotify_cid, redirect_uri=self._redirect_uri, scope=scope)
        # implicit.get_access_token()
        # self._spotify_token = implicit.get_cached_token()["access_token"]
        # print(f"yoooooo {token}")
        
        # self.spotify = spotipy.Spotify(client_credentials_manager=spotify_creds)
        
        # self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        # pkce = SpotifyPKCE(lient_id=self._spotify_cid, client_secret=self._spotify_csecret, redirect_uri=self._redirect_uri)

        # self._spotify_token_uri = self._spotify_dict["oauth2Providers"]["spotify"]["auth_uri"]
        # self._spotify_headers = self.set_spotify_headers()
        # self._spotify_params = {}
        # self._spotify_params["grant_type"] = "client_credentials"
        # self.spotify_token = self.get_spotify_token()
        # print(f"token: {self.spotify_token}")

    # def set_spotify_headers(self):
       # headers = {}
       #  Basic <base64 encoded client_id:client_secret>
       # field= f"{self._spotify_cid}:{self._spotify_csecret}"
       # field_bytes = base64.b64encode(field.encode("ascii")).decode("ascii")
       # headers["authorization"] = f"Basic {field_bytes}"

    # def get_spotify_token(self): 
        # r = requests.post(self._spotify_token_uri, headers=self._spotify_headers, data=self._spotify_params)
        # r = requests.post(self._spotify_token_uri, data=self._spotify_params, auth=(self._spotify_cid, self._spotify_csecret))
        # print(f"wtf -------- {r.text}")
        # print(f" print req output: {r.json()}")
        # return r.json()["access_token"]

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


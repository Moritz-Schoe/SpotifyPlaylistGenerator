import json
import os
import alive_progress
import ratelimit
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class PlaylistManager:

    def __init__(self):
        # Define your Spotify API credentials and settings
        self.username = os.getenv('SPOTIFY_USERNAME')
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_url = os.getenv('REDIRECT_URL')
        scope = 'user-library-read playlist-modify-public playlist-modify-private user-library-modify'
        self.lastfm_api_key = os.getenv('LASTFM_API_KEY')
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_url,
                                                            scope=scope))

    @ratelimit.limits(calls=10, period=1)
    def get_user_songs(self):
        # Get the user's saved tracks
        saved_tracks = []
        saved_track_uris = set()  # Maintain a set to check for duplicates
        offset = 0  # Initialize the offset for pagination

        with alive_progress.alive_bar(100, force_tty=True) as bar:
            while True:
                results = self.sp.current_user_saved_tracks(limit=50, offset=offset)

                if not results['items']:
                    break  # No more tracks to fetch

                for idx, item in enumerate(results['items']):
                    track = item['track']
                    track_uri = track['uri']

                    # Check if the track URI is already in the set of saved URIs
                    if track_uri not in saved_track_uris:
                        saved_tracks.append({
                            'track_name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'album_name': track['album']['name'],
                            'release_date': track['album']['release_date'],
                            'uri': track_uri
                        })
                        saved_track_uris.add(track_uri)  # Add the URI to the set

                offset += len(results['items'])
                bar()

        # Save the list of saved tracks as a JSON file
        json_filename = 'saved_tracks.json'
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(saved_tracks, json_file, ensure_ascii=False, indent=4)

        print(f'Saved {len(saved_tracks)} tracks to {json_filename}')

    @ratelimit.limits(calls=10, period=1)
    def get_track_genre(self, track_name, artist_name, track_uri):
        # Get the top tags for the track using the Last.fm API
        try:
            url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={self.lastfm_api_key}&artist={artist_name}&track={track_name}&format=json'
            response = requests.get(url)
            data = response.json()
            if 'toptags' in data['track']:
                return [tag['name'] for tag in data['track']['toptags']['tag']]
            else:
                return self.get_track_genre_from_spotify(track_uri)
        except:
            return self.get_track_genre_from_spotify(track_uri)

    @ratelimit.limits(calls=10, period=1)
    def get_track_genre_from_spotify(self, track_uri):
        # Fetch detailed information about the track using the Spotify API
        track_info = self.sp.track(track_uri)

        if track_info:
            # Extract genre information from the first artist's genres
            artist_genres = self.sp.artist(track_info['artists'][0]['uri'])['genres']

            if artist_genres:
                return artist_genres
            else:
                return []
        else:
            print(f"Track information for {track_uri} not available.")
            return []

    @ratelimit.limits(calls=10, period=1)
    def get_track_metadata(self, uri):
        # Get the URI of the track you want to analyze
        track_uri = uri

        # Read existing JSON data or initialize as an empty list if the file doesn't exist
        json_filename = 'track_info.json'
        existing_data = []

        try:
            with open(json_filename, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
        except FileNotFoundError:
            pass

        # Check if the track URI is already in the existing data
        if any(track_uri in track_data for track_data in existing_data):
            return

        # Fetch detailed information about the track using the Spotify API
        track_info = self.sp.track(track_uri)

        if track_info:
            # Fetch audio features for the track using the Spotify API
            audio_features = self.sp.audio_features(track_uri)

            if audio_features:
                # Extract relevant information
                info_dict = {
                    'track_name': track_info['name'],
                    'artist': [artist['name'] for artist in track_info['artists']],
                    'album': track_info['album']['name'],
                    'duration_ms': track_info['duration_ms'],
                    'popularity': track_info['popularity'],
                    'genre': self.get_track_genre(track_info['name'], track_info['artists'][0]['name'], track_uri),
                    'audio_features': audio_features[0]  # Store all audio features
                }

                # Append the new information to the existing data
                existing_data.append({track_uri: info_dict})

                # Write the combined data back to the file
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

            else:
                print("Audio features not available for this track.")
        else:
            print("Track information not available.")

    def createPlaylist(self, playlistName, playlistDescription, playlistPublic):
        self.sp.user_playlist_create(self.sp.current_user()['id'], playlistName, public=playlistPublic,
                                     collaborative=False, description=playlistDescription)

    # TODO: method not working, need to fix
    def addsongtoplaylist(self, playlistID, songURIs):
        self.sp.playlist_add_items(playlistID, songURIs, 0)

    def getPlaylists(self):
        playlists = []
        offset = 0  # Initialize the offset for pagination

        while True:
            results = self.sp.current_user_playlists(limit=50, offset=offset)

            if not results['items']:
                break  # No more playlists to fetch

            for playlist in results['items']:
                playlists.append({
                    'playlist_name': playlist['name'],
                    'playlist_id': playlist['id']
                })
                print(playlist)

            offset += len(results['items'])

        print(playlists)

    @staticmethod
    def makeSongRecommendation():
        with open('track_info.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Ask the user for desired genres (comma-separated)
        desired_genres = input("Enter desired genres (comma-separated): ").split(",")

        # Ask for the desired audio feature value ranges (divided by 100)
        danceability_range = tuple(map(float, input("Enter the desired danceability range (min,max): ").split(",")))
        energy_range = tuple(map(float, input("Enter the desired energy range (min,max): ").split(",")))
        speechiness_range = tuple(map(float, input("Enter the desired speechiness range (min,max): ").split(",")))
        acousticness_range = tuple(map(float, input("Enter the desired acousticness range (min,max): ").split(",")))
        instrumentalness_range = tuple(
            map(float, input("Enter the desired instrumentalness range (min,max): ").split(",")))
        tempo_range = tuple(map(float, input("Enter the desired tempo range (min,max): ").split(",")))

        # Divide the ranges by 100 to match the audio feature scales
        danceability_range = tuple(val / 100 for val in danceability_range)
        energy_range = tuple(val / 100 for val in energy_range)
        speechiness_range = tuple(val / 100 for val in speechiness_range)
        acousticness_range = tuple(val / 100 for val in acousticness_range)
        instrumentalness_range = tuple(val / 100 for val in instrumentalness_range)

        for track in data:
            track_data = track[list(track.keys())[0]]

            # Check if any of the desired genres match the track's genres
            if any(desired_genre.strip().lower() in [genre.lower() for genre in track_data['genre']] for desired_genre
                   in desired_genres):
                # Check if audio feature values are within the desired range
                if (
                        danceability_range[0] <= track_data['audio_features']['danceability'] <= danceability_range[
                    1] and
                        energy_range[0] <= track_data['audio_features']['energy'] <= energy_range[1] and
                        speechiness_range[0] <= track_data['audio_features']['speechiness'] <= speechiness_range[1] and
                        acousticness_range[0] <= track_data['audio_features']['acousticness'] <= acousticness_range[
                    1] and
                        instrumentalness_range[0] <= track_data['audio_features']['instrumentalness'] <=
                        instrumentalness_range[1] and
                        tempo_range[0] <= track_data['audio_features']['tempo'] <= tempo_range[1]
                ):
                    print(track_data['track_name'])

    def getPlaylist(self):
        playlist_ids = []
        offset = 0

        while True:
            results = self.sp.current_user_playlists(limit=50, offset=offset)

            if not results['items']:
                break  # No more playlists to fetch

            for playlist in results['items']:
                playlist_ids.append(playlist['id'])

            offset += len(results['items'])

        # Print the playlist IDs
        for playlist_id in playlist_ids:
            print(f"Playlist ID: {playlist_id}")

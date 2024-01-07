import json
from PlaylistManager import PlaylistManager
from BasicDataAnalysis import FavoriteSongsAnalyzer
from alive_progress import alive_bar

def main():
    # Initialize the playlist manager with your Spotify API credentials
    playlist_manager = PlaylistManager()
    playlist_manager.getPlaylists()

    print("Updating saved tracks...")
    playlist_manager.get_user_songs()

    with open('saved_tracks.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    uris = [track['uri'] for track in data]

    # remove uris that are already stored in track_info.json
    with open('track_info.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    stored_uris = [list(track.keys())[0] for track in data]
    uris = [uri for uri in uris if uri not in stored_uris]

    print("Fetching metadata...")
    with alive_bar(len(uris), force_tty=True ) as bar:
        for uri in uris:
            playlist_manager.get_track_metadata(uri)
            bar()

    data_analysis = FavoriteSongsAnalyzer()
    data_analysis.analyze_genre_distribution()

    # playlist_manager.makeSongRecommendation()

if __name__ == "__main__":
    main()

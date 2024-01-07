import json

class FavoriteSongsAnalyzer:
    def __init__(self):
        self.favorite_songs_data = None
        self.json_filename = 'track_info.json'

    def load_favorite_songs(self):
        try:
            with open(self.json_filename, 'r', encoding='utf-8') as json_file:
                self.favorite_songs_data = json.load(json_file)
        except FileNotFoundError:
            self.favorite_songs_data = []

    def analyze_popular_songs(self):
        popular_songs = []
        for song_data in self.favorite_songs_data:
            song_uri = list(song_data.keys())[0]
            popularity = song_data[song_uri]['popularity']
            if popularity >= 90:  # Adjust the threshold as needed
                popular_songs.append({
                    'track_name': song_data[song_uri]['track_name'],
                    'artist': song_data[song_uri]['artist'],
                    'popularity': popularity,
                })
        return popular_songs

    def analyze_genre_distribution(self):
        genre_distribution2 = {}
        for song_data in self.favorite_songs_data:
            song_uri = list(song_data.keys())[0]
            genres = song_data[song_uri]['genre']
            for genre in genres:
                if genre in genre_distribution2:
                    genre_distribution2[genre] += 1
                else:
                    genre_distribution2[genre] = 1
            genre_distribution2 = dict(sorted(genre_distribution2.items(), key=lambda item: item[1], reverse=True))
            genre_distribution2 = dict(list(genre_distribution2.items())[:40])

            # remove unuseful genres
            if 'MySpotigramBot' in genre_distribution2:
                del genre_distribution2['MySpotigramBot']
            if '-1001819731063' in genre_distribution2:
                del genre_distribution2['-1001819731063']

        return dict(list(genre_distribution2.items())[:30])

    def anaylze_key_metric_averages(self):
        key_metrics = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness',
                       'tempo']
        key_metric_averages = {}
        for song_data in self.favorite_songs_data:
            song_uri = list(song_data.keys())[0]
            for metric in key_metrics:
                if metric in key_metric_averages:
                    key_metric_averages[metric] += song_data[song_uri]["audio_features"][metric]
                else:
                    key_metric_averages[metric] = song_data[song_uri]["audio_features"][metric]
        for metric in key_metrics:
            key_metric_averages[metric] /= len(self.favorite_songs_data)
            if metric == 'tempo':
                key_metric_averages[metric] = str(round(key_metric_averages[metric])) + " BPM"
            else:
                key_metric_averages[metric] = round(key_metric_averages[metric], 2) * 100
        return key_metric_averages



# Example usage:
if __name__ == "__main__":
    analyzer = FavoriteSongsAnalyzer()
    analyzer.load_favorite_songs()
    genre_distribution = analyzer.analyze_genre_distribution()
    print("\nHere's an overview of the genres you like to listen to:")
    for genre, count in genre_distribution.items():
        print(f"{genre}: {count} songs")

    print("\nHere some more interesting facts about the songs you like:\n")
    acoustic_features = analyzer.anaylze_key_metric_averages()
    for feature, value in acoustic_features.items():
        print(f"{feature.capitalize()}: {value}")

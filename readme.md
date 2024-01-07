# Spotify Playlist Generator from saved songs
**DISCLAIMER**: The project is currently under development and is **not fully functional**. Key issues are adressed later.

The aim of this project is to offer a Python-based solution for generating a Spotify playlist from "saved songs" based on user preferences.

Ultimately this could be utilized to automatically sort saved songs into playlists based on genre, mood, etc.


## Getting Started

To use this project, follow these steps:

### Prerequisites

- Python 3.x
- `requirements.txt` contains necessary Python packages. Install them via: pip install -r requirements.txt

### Setup

1. Clone the repository
2. Create a `.env` file in the root directory and add your API credentials:

```plaintext
SPOTIFY_USERNAME=your_spotify_username
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key
REDIRECT_URL=your_redirect_url
```

## How to navigate this project

The project is divided into three main parts:

1. **PlaylistManager.py**: Contains the `PlaylistManager` class, enabling interaction with Spotify playlists and tracks.

2. **BasicDataAnalysis.py**: Includes tools and methods for basic data analysis of favorite songs' data.

3. **main.py**: The main script to execute and demonstrate various project functionalities.

4. **.env**: Configuration file used for storing sensitive credentials like API keys using environment variables. This file is ignored by Git.

5. **saved_tracks.json**: A JSON file containing information about saved tracks fetched from Spotify.

6. **track_info.json**: A JSON file storing detailed metadata about tracks obtained during the execution of the script.

7. **requirements.txt**: Lists all Python dependencies required by the project. Install these dependencies using `pip install -r requirements.txt`.



## Key Issues
- Spotify API does not provide genre information for tracks. This is a key issue for this project as it is not possible to sort songs into playlists based on genre.
- The current workaround is to use the LastFM API to get genre information for tracks. However, this is not ideal as data is not always reliable and sometimes not available at all.
- The method addsongtoplaylist in PlaylistManager,py is currently not working. There seems to be an issue in the API. The current workaround is to print the song and artist names and manually add them to a playlist.


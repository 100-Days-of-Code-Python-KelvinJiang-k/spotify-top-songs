import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup


def main():
    selected_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

    song_name_list = get_top_songs(date=selected_date)

    spotify = authenticate_spotify()
    create_playlist(sp=spotify, song_names=song_name_list, date=selected_date)


def get_top_songs(date: str):
    URL = "https://www.billboard.com/charts/hot-100/"
    response = requests.get(f"{URL}{date}")
    billboard_html = response.text
    soup = BeautifulSoup(billboard_html, "html.parser")

    # removes all leading and trailing whitespace
    song_names = [' '.join(song.text.split()) for song in soup.select("div li ul li h3")]
    return song_names


def authenticate_spotify():
    SCOPE = "playlist-modify-private"
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    redirect_uri = os.environ["SPOTIPY_REDIRECT_URI"]
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=SCOPE,
                                  client_id=client_id,
                                  client_secret=client_secret,
                                  redirect_uri=redirect_uri))
    return sp


def get_song_uris(sp, song_names, date: str):
    year = date.split('-')[0]
    song_uris = []
    for name in song_names:
        track = sp.search(q=f"track: {name} year: {year}", limit=1, type="track")["tracks"]
        try:
            song_uri = track["items"][0]["uri"]
            song_uris.append(song_uri)
        except IndexError:
            print("Song is not on Spotify.")
    return song_uris


def create_playlist(sp, song_names, date: str):
    user_id = sp.current_user()["id"]
    song_uris = get_song_uris(sp=sp, song_names=song_names, date=date)

    playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
    sp.playlist_replace_items(playlist_id=playlist["id"], items=song_uris)


if __name__ == "__main__":
    main()

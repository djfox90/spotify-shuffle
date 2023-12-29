import os

import spotipy
import streamlit as st
import json
import requests
from dotenv import load_dotenv

load_dotenv()

@st.cache_data
def get_spotify_client(authorization_code):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:8501",
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    return spotipy.Spotify(auth=response.json()["access_token"])
def login_spotify():
    auth_url =  f"https://accounts.spotify.com/authorize?client_id={os.environ['CLIENT_ID']}&response_type=code&redirect_uri=http://localhost:8501&scope=playlist-modify-private"
    query_param = st.experimental_get_query_params()
    if query_param:
        return query_param["code"][0]
    st.write(
        f"Please log in to <a target='_self' href='{auth_url}'>spotify",
        unsafe_allow_html=True,
    )
    query_param = st.experimental_get_query_params()
    if query_param:
        return query_param["code"][0]

def main():
    authorization_code = login_spotify()
    if not authorization_code:
        return
    spotify_client = get_spotify_client(authorization_code)
    
    with st.form("Playlist generation"):
        prompt = st.text_input("Describe the music you'd like to hear..")
        song_count = st.slider("Songs", 1, 30, 10)
        submitted = st.form_submit_button("Create")
    playlist_name = "test"
    playlist_description = "test create"    
    user_id = spotify_client.me()['id']
    playlist = spotify_client.user_playlist_create(
        user_id,playlist_name,False,description=playlist_description
    )
    playlist_id = playlist['id']
    print(playlist_id)
    
    
    
   
    
    
if __name__ == "__main__":
    main()
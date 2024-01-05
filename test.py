import os
import base64
import spotipy
import streamlit as st
import json
import requests
import numpy as np
import random
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


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
    auth_url = f"https://accounts.spotify.com/authorize?client_id={os.environ['CLIENT_ID']}&response_type=code&redirect_uri=http://localhost:8501&scope=playlist-modify-public"
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


def request_auth():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {"grant_type": "client_credentials"}
    res = requests.post(url, headers=headers, data=params)
    json_res = json.loads(res.content)
    token = json_res["access_token"]

    return token


def get_header(token):
    return {"Authorization": "Bearer " + token}


def search_artist(token, name):
    url = "https://api.spotify.com/v1/search"
    headers = get_header(token)
    query = f"?q={name}&type=artist&limit=1"
    query_url = url + query

    res = requests.get(query_url, headers=headers)
    json_res = json.loads(res.content)["artists"]["items"]
    print(json_res)
    if len(json_res) == 0:
        return None
    else:
        return json_res[0]


def playlist_id(token,playlist_name):
    url = "https://api.spotify.com/v1/"

    headers = get_header(token)
    query = "users/djfox90/playlists"
    query_url = url + query

    res = requests.get(query_url, headers=headers)
    json_res = json.loads(res.content)["items"]

    for i in range(len(json_res)):
        if json_res[i]["name"] == playlist_name:
            playlist_id = json_res[i]["id"]

    return playlist_id


def playlist_songs(token, playlist_id):
    url = "https://api.spotify.com/v1/"
    headers = get_header(token)
    query = "playlists/" + playlist_id + "/tracks"
    query_url = url + query

    res = requests.get(query_url, headers=headers)
    json_res = json.loads(res.content)["items"]
    total_next = json.loads(res.content)["next"]
    total_songs = json.loads(res.content)["total"]
    random_playlist = np.full(shape=total_songs, fill_value="0", dtype=object)

    offset = "0"
    if total_next != None:
        offset = "100"
    next_string = (
        "https://api.spotify.com/v1/playlists/4k7YATTCAkMVJoArqc8xbn/tracks?offset="
        + offset
        + "&limit=100"
    )

    res_next = requests.get(next_string, headers=headers)

    count = 0

    exit = False

    while exit != True:
        for i in range(len(json_res)):
            rand_exit = False
            while rand_exit != True:
                random_num = random.randint(0, total_songs - 1)

                if random_playlist[random_num] == "0":
                    random_playlist[random_num] = json_res[i]["track"]["uri"]
                    rand_exit = True

        if total_next == None:
            exit = True
        else:
            res_next = requests.get(next_string, headers=headers)
            json_res = json.loads(res_next.content)["items"]
            offset = int(offset) + 100
            offset = str(offset)
            next_string = (
                "https://api.spotify.com/v1/playlists/4k7YATTCAkMVJoArqc8xbn/tracks?offset="
                + offset
                + "&limit=100"
            )
            total_next = json.loads(res_next.content)["next"]

    return random_playlist


def main():
    authorization_code = login_spotify()
    if not authorization_code:
        return
    spotify_client = get_spotify_client(authorization_code)

    with st.form("Playlist generation"):
        prompt = st.text_input("Input playlist you would like to shuffle")
        submitted = st.form_submit_button("Create")
    if not submitted:
        return
    playlist_name = prompt + " test"
    playlist_description = "test create"
    user_id = spotify_client.me()["id"]
    playlist = spotify_client.user_playlist_create(
        user_id, playlist_name, True, description=playlist_description
    )
    playlist_i = playlist["id"]
    old_playlist = playlist_id(request_auth(),prompt)
    print(old_playlist)
    random_playlist = playlist_songs(request_auth(), old_playlist)

    sub = "lo"
    count = 0
    for i in range(len(random_playlist)):
        t = [random_playlist[i]]

        if sub not in random_playlist[i]:
            spotify_client.playlist_add_items(
                playlist_id=playlist_i, items=t, position=count
            )
            count = count + 1
    st.write(
        f"Shuffled Playlist Created <a href='{playlist['external_urls']['spotify']}'>Click Here</a>",
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()

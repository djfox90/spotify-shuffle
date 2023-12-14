from dotenv import load_dotenv, find_dotenv
import base64
import os
import json
import requests as rq

load_dotenv(find_dotenv())

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


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
    res = rq.post(url, headers=headers, data=params)
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

    res = rq.get(query_url, headers=headers)
    json_res = json.loads(res.content)["artists"]["items"]
    print(json_res)
    if len(json_res) == 0:
        return None
    else:
        
        return json_res[0]
    
def playlist_id(token):
    
    url = "https://api.spotify.com/v1/"
    
    headers = get_header(token)
    query = "users/djfox90/playlists"
    query_url = url + query

    res = rq.get(query_url, headers=headers)
    json_res = json.loads(res.content)['items']
    for i in range(len(json_res)):
        if json_res[i]['name'] == 'Test':
            print('yes')
            playlist_id = json_res[i]['id']
            print(playlist_id)
        else:
            print('nop')

    print("here")
    
    
    

playlist_id(request_auth())
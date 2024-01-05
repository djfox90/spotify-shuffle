from dotenv import load_dotenv, find_dotenv
import base64
import os
import json
import requests as rq
import spotify1
from fastapi.responses import HTMLResponse
import numpy as np
import random



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
        if json_res[i]['name'] == 'Lex':
          
            playlist_id = json_res[i]['id']
      
    return playlist_id

   
def playlist_songs(token,playlist_id):
    
    url = "https://api.spotify.com/v1/"
    headers = get_header(token)
    query = "playlists/" + playlist_id + "/tracks"
    query_url = url + query

    res = rq.get(query_url, headers=headers)
    json_res = json.loads(res.content)['items']
    print(json_res[0]['track']['uri'])
    total_next = json.loads(res.content)["next"]
    total_songs = json.loads(res.content)["total"]
    random_playlist = np.full(shape=total_songs,fill_value="0",dtype=object)
    

    offset = "0"
    if total_next != None:
        offset = "100"
    next_string = "https://api.spotify.com/v1/playlists/4k7YATTCAkMVJoArqc8xbn/tracks?offset=" + offset + "&limit=100"   

    res_next = rq.get(next_string, headers=headers)
   
    count = 0
  
    
    exit = False
    
    while  exit != True:
        
        for i in range(len(json_res)):
            rand_exit = False
            while rand_exit != True:
                random_num = random.randint(0,total_songs-1)
               
                if random_playlist[random_num] == "0":
                    random_playlist[random_num] = json_res[i]['track']['name']
                    rand_exit = True
                    
            
            
        if total_next == None:
            exit = True
        else:
            res_next = rq.get(next_string, headers=headers)
            json_res = json.loads(res_next.content)['items']
            offset = int(offset) + 100
            offset = str(offset)
            next_string = "https://api.spotify.com/v1/playlists/4k7YATTCAkMVJoArqc8xbn/tracks?offset=" + offset + "&limit=100" 
            total_next = json.loads(res_next.content)["next"]
            
    print(random_playlist)


playlist=playlist_id(request_auth())

playlist_songs(request_auth(),playlist)

#create_playlist(request_auth())
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
import base64
import requests
import urllib.parse

def search(artist="Hozier"):
    client_id="0f384b93d54841a4bbb63fc3c414320e"
    client_secret="6738a64f4837459fa582348bc557d592"

    encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
    token_headers = {
        "Authorization": "Basic " + encoded_credentials
    }
    token_data = {
        "grant_type": "client_credentials"
    }
    
    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
    access_token = r.json()["access_token"]
    
    success = True
    base="https://api.spotify.com"
    try:
    #search //GET Spotify Artist ID    
        parameters = "/v1/search?"+urllib.parse.urlencode({"q":artist,"type":"artist", "access_token":access_token})
        search_artists_id_url=base+parameters
        answer = requests.get(search_artists_id_url).json()
        artist_id= answer["artists"]["items"][0]["id"]        
    except:
        success = False
    if success:
    #GET artist info
        parameters="/v1/artists/"+artist_id+"?"+urllib.parse.urlencode({"access_token":access_token})
        get_artist_info = base+parameters 
        
        answer = requests.get(get_artist_info).json() 

        artist_url=answer["external_urls"]["spotify"]
        artist_genres=answer["genres"]
        artist_image=answer["images"][0]["url"]
        
        artist_info = {"name":artist,"url":artist_url,"genres":artist_genres,"image":artist_image}

        #GET all artist's albums
        parameters="/v1/artists/"+artist_id+"/albums?"+urllib.parse.urlencode({"access_token":access_token,"include_group" : "album"})
        get_all_albums = base+parameters
        albums_info=[]
        answer = requests.get(get_all_albums).json()    
        for item in answer["items"]:
            albums_info.append({'name':item["name"],'cover':item["images"][0]["url"],'release':item["release_date"],'numTracks':item["total_tracks"]})
        return albums_info, artist_info
    return {},{}
    
def index_page(request):
    submitbutton= request.POST.get("submit")
    artist_name = ""
    if submitbutton:
        artist_name=request.POST['artist']
    albumsInfo,artistInfo=search(artist_name)
    context = {
        'albums': albumsInfo,
        'artist':artistInfo,
    }
    return render(request,"index.html",context)


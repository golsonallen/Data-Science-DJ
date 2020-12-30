from secrets import ClientID
from secrets import ClientSecret
import requests
import base64
import json
import pandas as pd

class Data:

    def __init__(self):
        self.ID = ClientID
        self.Secret = ClientSecret

    #Need to include a Base 64 encoded string that contains the client ID and client secret key with the request
    def base64Encode(self):
        message = self.ID + ":" + self.Secret
        #convert message to a bytes-like object
        message_bytes = message.encode('ascii')
        #base64 encode the bytes
        base64_bytes = base64.b64encode(message_bytes)
        #decoding the bytes as ascii to get a string representation
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    #Request authorization, gain access token
    def authorize(self, encodedAuth: str):
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic {}".format(encodedAuth)
        }
        body = {
            "grant_type": "client_credentials"
        }
        response = requests.post(url = url, headers = headers, data = body)
        self.token = response.json()["access_token"]
        #TO DO: figure out how to handle expiration time of token

    def getPlaylistID(self, playlistURL: str):
        playlistID = playlistURL.split("/")[-1]
        return playlistID

    #uses the Get a Playlist's Items endpoint but only to check the total number
    #of track in the playlist
    def getPlaylistLength(self, playlistID: str):
        url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        headers = {
            "Authorization": "Bearer {}".format(self.token),
        }
        params = {
            #only need one track item since we are only looking at the playlist's length
            #and not what's in the playlist
            "limit": "1"
        } 
        response = requests.get(url = url, headers = headers, params=params)
        playlistLength = response.json()["total"]
        return playlistLength

    #returns a list of track objects
    def getPlaylistItems(self, limit: int, offset: int, playlistID: str):
        url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        headers = {
            "Authorization": "Bearer {}".format(self.token),
        }
        params = {
            "limit": str(limit),
            "offset": str(offset)
        } 
        response = requests.get(url = url, headers = headers, params=params)
        items = response.json()["items"]
        return items

    #limit on tracks to return is capped at 100 so playlist length will dictate
    #the way to get all of the tracks in the playlist
    def getCompletePlaylist(self, playlistID: str, playlistLength: int):
        #can get all items in just one request
        if playlistLength <= 100:
            totalTrackList = self.getPlaylistItems(limit = playlistLength, offset = 0, playlistID = playlistID)
            return totalTrackList
        #need to make multiple requests and update offset (index of first item to return)
        #each time since playlist length is over the limit
        else:
            totalTrackList = []
            iterations = playlistLength // 100
            remainder = playlistLength % 100
            offset = 0
            for _ in range(iterations):
                trackList = self.getPlaylistItems(limit = 100, offset = offset, playlistID = playlistID)
                for track in trackList:
                    totalTrackList.append(track["track"])
                offset += 100
            trackList = self.getPlaylistItems(limit = remainder, offset = playlistLength - remainder, playlistID= playlistID)
            for track in trackList:
                totalTrackList.append(track["track"])
            return totalTrackList
            
    def createSongDataFrame(self, totalTrackList: list):
        self.df = pd.DataFrame(totalTrackList)
        self.df = self.df[["name", "id", "duration_ms", "explicit", "popularity", ]]

    def addAudioFeatures(self):
        headers = {
            "Authorization": "Bearer {}".format(self.token),
        }
        #use first track to construct a dataframe
        initalURL = "https://api.spotify.com/v1/audio-features/{}".format(self.df["id"][0])
        initial_trackID_response = requests.get(url = initalURL, headers = headers)
        features_df = pd.DataFrame.from_records([initial_trackID_response.json()])

        #form a complete df of audio features by adding the rest of the tracks
        for trackID in self.df["id"][1:]:
            url = "https://api.spotify.com/v1/audio-features/{}".format(trackID)
            response = requests.get(url = url, headers = headers)
            temp_df = pd.DataFrame.from_records([response.json()])
            features_df = features_df.append(temp_df, ignore_index = True)
        #join self.df with features df
        self.df = self.df.merge(features_df, on = "id")

    def addAudioAnalysis(self):
        

    def main(self):
        pass


if __name__ == "__main__":
    data = Data()
    encodedAuth = data.base64Encode()
    data.authorize(encodedAuth)
    playlistID = data.getPlaylistID("https://open.spotify.com/playlist/7ppwau1XzaZvvW6qnBbjuE")
    #print(playlistID)
    playlistLength = data.getPlaylistLength(playlistID)
    #print(playlistLength)
    tracklist = data.getCompletePlaylist(playlistID, playlistLength)
    #print(json.dumps(playlistItems, indent=4))
    data.createSongDataFrame(tracklist)
    data.addAudioFeatures()
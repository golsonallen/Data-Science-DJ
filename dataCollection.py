from secrets import ClientID
from secrets import ClientSecret
from math import ceil
import requests
import base64
import json
import pandas as pd

class DataCollector:

    def __init__(self) -> None:
        self.ID = ClientID
        self.Secret = ClientSecret
        self.token = ""
        self.df = pd.DataFrame()

    #Need to include a Base 64 encoded string that contains the client ID and client secret key with the request
    def base64Encode(self) -> str:
        message = self.ID + ":" + self.Secret
        #convert message to a bytes-like object
        message_bytes = message.encode('ascii')
        #base64 encode the bytes
        base64_bytes = base64.b64encode(message_bytes)
        #decoding the bytes as ascii to get a string representation
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    #Request authorization, gain access token
    def authorize(self, encodedAuth: str) -> None:
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

    def getPlaylistID(self, playlistURL: str) -> str:
        playlistID = playlistURL.split("/")[-1]
        return playlistID

    #uses the Get a Playlist's Items endpoint but only to check the total number
    #of track in the playlist
    def getPlaylistLength(self, playlistID: str) -> int:
        url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        headers = {
            "Authorization": "Bearer {}".format(self.token),
        }
        params = {
            #only need one track item since we are only looking at the playlist's length
            "limit": "1"
        } 
        response = requests.get(url = url, headers = headers, params=params)
        #playlist Length
        return response.json()["total"]

    #returns a list of track objects
    def getPlaylistItems(self, limit: int, offset: int, playlistID: str) -> list:
        url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        headers = {
            "Authorization": "Bearer {}".format(self.token),
        }
        params = {
            "limit": str(limit),
            "offset": str(offset)
        } 
        response = requests.get(url = url, headers = headers, params=params)
        return response.json()["items"]

    #iterate through each track object and extract only the key info
    #return a list containing a dictionary for each track's info
    def extractSongsFromPlaylistItems(self, items: list) -> list:
        track_info_list = []
        for track_item in items:
            key_info = {}
            trackDict = track_item["track"]
            key_info["name"] = trackDict["name"]
            key_info["id"] = trackDict["id"]
            key_info["duration_ms"] = trackDict["duration_ms"]
            key_info["explicit"] = trackDict["explicit"]
            key_info["popularity"] = trackDict["popularity"]

            track_info_list.append(key_info)
        return track_info_list

    #limit on tracks to return is capped at 100 so playlist length will dictate
    #the way to get all of the tracks in the playlist
    def getCompletePlaylist(self, playlistID: str, playlistLength: int) -> list:
        #can get all items in just one request
        if playlistLength <= 100:
            items = self.getPlaylistItems(limit = playlistLength, offset = 0, playlistID = playlistID)
            #return list containing a dict for every song in the playlist
            return self.extractSongsFromPlaylistItems(items)
        #need to make multiple requests and update offset (index of first item to return)
        #each time since playlist length is over the limit
        else:
            finalList = []
            iterations = ceil(playlistLength / 100)
            offset = 0
            for _ in range(iterations):
                items = self.getPlaylistItems(limit = 100, offset = offset, playlistID = playlistID)
                #need to add the track list from each iteration to a master list containing info for every track
                finalList += self.extractSongsFromPlaylistItems(items)
                offset += 100
            return finalList
            
    def createSongDataFrame(self, totalTrackList: list) -> None:
        self.df = pd.DataFrame(totalTrackList)

    def addAudioFeatures(self):
        features_df = pd.DataFrame()
        for trackID in self.df["id"]:
            url = "https://api.spotify.com/v1/audio-features/{}".format(trackID)
            response = requests.get(url = url, headers = {"Authorization": "Bearer {}".format(self.token)})
            temp_df = pd.DataFrame.from_records([response.json()])
            features_df = features_df.append(temp_df, ignore_index = True)
        #join self.df with features df
        self.df = self.df.merge(features_df, on = "id")

    #takes audio analysis dict as parameter and returns dictionary of 
    #only the important features and their values 
    def addAudioAnalysisHelper(self, responseDict, trackID: str) -> dict:
        trackDict = responseDict["track"]

        audioDict = {"id": trackID}
        audioDict["end_of_fade_in"] = trackDict["end_of_fade_in"]
        audioDict["start_of_fade_out"] = trackDict["start_of_fade_out"]
        audioDict["analysis_sample_rate"] = trackDict["analysis_sample_rate"]
        return audioDict

    def addAudioAnalysis(self) -> None:
        analysis_df = pd.DataFrame()
        for trackID in self.df["id"]:
            url = "https://api.spotify.com/v1/audio-analysis/{}".format(trackID)
            response = requests.get(url = url, headers = {"Authorization": "Bearer {}".format(self.token)})
            tempDict = self.addAudioAnalysisHelper(response.json(), trackID)
            temp_df = pd.DataFrame.from_records([tempDict])
            analysis_df = analysis_df.append(temp_df, ignore_index = True)
        #join self.df with analysis df
        self.df = self.df.merge(analysis_df, on = "id")

    def main(self, playlistURLs: list) -> None:
        #empty df that will hold the data from all the playlists combined
        df1 = pd.DataFrame()
        encodedAuth = self.base64Encode()
        self.authorize(encodedAuth)
        for url in playlistURLs:
            playlistID = self.getPlaylistID(url)
            playlistLength = self.getPlaylistLength(playlistID)
            tracklist = self.getCompletePlaylist(playlistID, playlistLength)
            self.createSongDataFrame(tracklist)
            self.addAudioFeatures()
            self.addAudioAnalysis()

            #add each individual playlist df to main df
            df1 = df1.append(self.df, ignore_index = True)
            
        df1.to_csv("song_data.csv", index = False)


if __name__ == "__main__":
    with open("playlist_links.txt", "r") as playlist_links:
        #get rid of "\n" from each url
        urls = playlist_links.read().splitlines()

    data = DataCollector()
    data.main(urls)
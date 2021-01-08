# Data Science DJ - Griffin Olson-Allen

# About
## Data Science Project Examining Electonic Dance Music Songs
This project contains 4 files.
1. **playlist_links.txt**: links to the EDM playlists on Spotify I used for the data
2. **dataCollection.py**: a script to get all the data from the Spotify playlist
3. **song_data.csv**: song data
4. **DJ.ipynb**: cleaning, visualizing, and making predictions from the data.

# playlist_links.txt
I searched Spotify for different EDM (Electronic Dance Music) playlists and picked a few of the ones with the most likes and most songs in them to use for song data. Replace the playlist links with different ones to generate your own song data.

# dataCollection.py
This file is the actual program to use the playlist list to gather song data. I used the Spotify API extensively. First, I extracted the songs from each playlist and a few characteristics of the song to form a massive song list. Then, for each song, I used the Spotify API to get every song's audio features and audio analysis. The final product was song_data.csv

# song_data.csv
The dataset I used for the project: 1038 instances and 26 features.

**NOTE:** The CSV file might be shorter than expected. The number of lines in the CSV could be less than the sum of the number of songs in each playlist. Missing songs are because songs in the playlists used might be unavailable in your country or region. This is usually because of licensing/record label/artist requests.

# DJ.ipynb
The notebook is the bulk of the project. This is where I complete data cleaning, visualization, and song popularity prediction. There are plenty of comments and notes where I explain my thought process and observations.

1. Cleaning - I dropped duplicate or unnecessary features and did a tiny bit of feature engineering.

2. Visualizing - I mostly used Seaborn to visualize the data. I looked for general trends in the songs and trends between features I thought would be related. I also tried to compare the distribution of certain features to what would be expected of electronic dance music. 

3. Prediction - I used two models to try and predict a song's popularity: a Linear Regression and a Support Vector Regression. Both performed pretty poorly and had high error rates. With popularity on a scale of 0-100, on average, I was off by 17 with the Linear Regression and 16 with the Support Vector Regression. R squared for both was close to 0. 

# Reflection
I believe the distribution and subjectiveness of popularity were what made it so difficult to predict. More than 10% of the songs in my dataset had a popularity of 0. This goes hand in hand with the subjectiveness of popularity. Spotify calculates a song's popularity:
> based, for the most part, on the total number of plays the track has had and how recent those plays are. Generally speaking, songs that are being played a lot now will have higher popularity than songs that were played a lot in the past. 

So a song that I predict to have a popularity of 70, based on its features, might have been a 65 a month ago, but people have stopped listening to it as much and it's now a 45. I also used a playlist titled "EDM Hits 2012-2021" and most of the 0 or very low popularity songs were probably the older songs from this playlist. 

# Possible Issues
One thing to be aware of when trying to collect the data from the inputted playlist links is that it takes a *while*. Grabbing 1000 songs from Spotify, and then getting audio features and analysis for every song takes time. Another issue I ran into was when I kept running the collection program multiple times in a short time frame. I would get a 503 error code which the Spotify API describes as:
> Service Unavailable - The server is currently unable to handle the request due to a temporary condition which will be alleviated after some delay. You can choose to resend the request again.

Usually, when I just took a break for an hour or so it would work fine again. 

# Improvements
- break up playlist links and go one at a time, then combine each CSV to prevent 503 error
- utilize Get Audio Features for Several Tracks Endpoint to reduce the number of API calls and improve speed
- token refresh
- use release date and artist as features
- use more audio analysis features (didn't use ones with confidence values attached)
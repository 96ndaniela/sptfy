# sptfy

**“Generate Spotify Recommendations”**

You will be evaluated on all the following characteristics: clarity/communication, creativity,
data management, exploratory data analysis, modeling and business value. You have to use
Python to process the dataset and to generate the solution, but you are free to choose any
libraries and other tools you may need.
You can use any framework tool for visualization you feel comfortable with (take into
account that you’ll need to give viewer access to at least 5 members of our team).
Use every dataset given to build your solution, you are free to add external information for
your analysis.
The solution has to be uploaded to a Github repository and provide access for our team
members.

**Context**
Assume you have to present your results to a Data Science Team and also a Marketing Team and
their manager.
In general, musical tastes often differ quite drastically from what is popular in the mainstream to
what any person chooses to listen to everyday.
1. The main task is to create new recommendations for 4 users in our team. All you have is a
playlist they have created and currently listen to.
2. The solution must have 2 new recommendations for these users, one has to be a playlist
already created in the dataset and the second has to be a completely new playlist.
3. You can use all the information in the dataset to create recommendations. Take into
account the text columns to enrich the features available.
a. A good starting point is that you have popularity scores for each song. How can you
use this scoring to create recommendations?
4. Provide a clear explanation on how you will measure the quality of your recommendations.
5. Use Docker for reproducibility and make sure we can validate your solution.
Note. When presenting your solution you will be given a new playlist corresponding to an
unknown user for you to show the pipeline created to generate a new recommendation.


### logic
```
── user input should be from 4 users (.csv) or a new file that has at least: id, song's name & artist
── must find existing playlist in dataset ( playlist_name ) & another that matches the average tempo for all songs
── shows possible song recommendations based in popularity to meet context 3.a : *a good starting point is that you have popularity scores for each song. how can you use this scoring to create recommendations?*
── should return top 10 tracks: keypoint being, not in the list, fulfilling 3.a
── needs to have tempo similarity for user's current preferences + popularity score of the songs ( rank new suggestions )
```

## structure

```
sptfy
s t r e a m l i t & d o c k e r 
── data/                  # all data ( csvs, dataset to work with )  
── main.py                # recommendation system 
── tempo.py               # recommendation functions based on tempo + ranking
── requirements.txt       # packages
── Dockerfile             # config
```
 

### visualization
```
── currently public, available to see & work with on : https://spotifyrecs.streamlit.app/
── works with docker ( +++ )
     git clone https://github.com/96ndaniela/sptfy.git
     cd sptfy
     docker build -t sptfy .
     docker run -p 8501:8501 sptfy
── visit : http://localhost:8501 in your browser to access the app.
```

### documentation
```
── streamlit + python : https://www.datacamp.com/tutorial/streamlit & https://docs.streamlit.io/develop/api-reference
── streamlit + docker : https://docs.streamlit.io/deploy/tutorials/docker
── streamlit + visuals / better performance : https://docs.streamlit.io/develop/api-reference/media/st.image
```

### choosing tempo-popularity vs. other features
```
── on tempo: the bpm determines the energy & pacing of a song. it's intuitive when choosing music for specific contexts; it's also stable and interpretable across genres. lastly, it works well without abrupt rhythmic shifts if there will be changes in artists.
── on popularity: not only is derived from user engagement but it helps surface tracks users are more likely to enjoy and recognize, while also filtering out low-quality songs that may not align with the listener's expectations.

other features:
── danceability can be subjective and genre-dependent; can overlap with tempo but not always align with user expectations.
energy's too broad and often redundant with tempo.
── loudness, realistically, is not very helpful for playlist flow ( moreso considering spotify itself is already normalizing this through the platform )
── speechiness can actually be useful for podcasts or spoken-word, but not for general music playlists.
── acousticness would be too narrow or misleading across genres.
── mode / key / instrumentalness / valence / duration : they are songs' information, but technically, they're not always noticeable or meaningful when choosing a song itself based on preference.

furthermore, the idea would be that you get recommendations that are as diverse as spotify can possibly give ─ thus, it's important to mention that, from all the data given in the csv ( dataframe ), tempo has the most unique counts to choose from ( at 10180 ). this would allow to have diverse songs that go across all the possible tempos that are available in the platform.

 
 ( https://i.imgur.com/otH27BV.jpeg )

```
 

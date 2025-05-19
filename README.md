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

## structure

```
sptfy
── data/                  # all data ( csvs, dataset to work with )  
── main.py                # recommendation system
── tempo.py               # recommendation functions based on tempo + ranking
── requirements.txt       # packages
── Dockerfile             # config
```

### to do 
```
── run local 
── make visual prettier bro, sike
── test again with a dummy csv
── cry more
```

### logic
```
── user input should be from 4 users (.csv) or a new file that has at least: id, song's name & artist
── must find existing playlist in dataset ( playlist_name ) & another that matches the average tempo for all songs
── shows possible song recommendations based in popularity to meet context 3.a : *a good starting point is that you have popularity scores for each song. how can you use this scoring to create recommendations?*
── should return top 10 tracks: keypoint being, not in the list, fulfilling 3.a
── needs to have tempo similarity for user's current preferences + popularity score of the songs ( rank new suggestions )
```

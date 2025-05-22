import pandas as pd
import numpy as np
from rapidfuzz import fuzz

# all features available for comparison on recommendations
FEATURE_COLUMNS = [
    'tempo', 'danceability', 'energy', 'key', 'loudness', 'mode',
    'speechiness', 'acousticness', 'liveness', 'popularity'
]

def load_sptfy(filepath, playlist_with=10):
    df = pd.read_csv(filepath)

    rename_map = {
        'track_name': 'name',
        'track_artist': 'artists',
        'track_popularity': 'popularity',
        'track_id': 'id',
        'tempo': 'tempo',
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    required_cols = ['id', 'name', 'artists', 'tempo', 'popularity', 'playlist_name']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"missing columns in spotify csv: {missing}")

    df = df.drop_duplicates(subset=['id'])
    df = df.dropna(subset=['tempo', 'popularity'])
    df = df.reset_index(drop=True)
    return df

def enrich_user_playlist(user_df, spotify_df):
    # first requirements : user-provided playlist has to have the required columns ( min. 3 )
    if not all(col in user_df.columns for col in ['Id', 'Song', 'Artist']):
        raise KeyError("user playlist must contain 'Id', 'Song', 'Artist' columns.")
    # normalize column names
    user_df = user_df.rename(columns={'Id': 'id', 'Song': 'name', 'Artist': 'artists'})
    # merge by id first
    merged = pd.merge(user_df, spotify_df, on='id', how='left', suffixes=('_user', ''))

    # find entries missing any key audio features
    missing_data = merged[merged[FEATURE_COLUMNS].isnull().any(axis=1)]
    return merged

    # list to store fuzzy-matched rows for missing data if any
    enriched_rows = []
    if not missing_data.empty:
        enriched_rows = []
        # if there's a missing row, try to find a best fuzzy match based on song name and artist
        for _, user_row in missing_data.iterrows():
            best_match = None
            best_score = 0
            for _, spot_row in spotify_df.iterrows():
                # fuzzy match song title and artist separately
                score_name = fuzz.partial_ratio(user_row['name'], spot_row['name'])
                score_artist = fuzz.partial_ratio(user_row['artists'], spot_row['artists'])
                # combines scores to get a total similarity
                total_score = (score_name + score_artist) / 2
                # keep the match only if it's better than previous ones and above 
                if total_score > best_score and total_score > 85:
                    best_match = spot_row
                    best_score = total_score
            # add the best match (s) if a confident one is found        
            if best_match is not None:
                enriched_rows.append(pd.DataFrame([best_match]))
        # combine valid original matches and fuzzy matches
        enriched_df = merged.dropna(subset=FEATURE_COLUMNS)
        # add any fuzzy-matched w/ no duplicate ids
        if enriched_rows:
            fuzzy_df = pd.concat(enriched_rows, ignore_index=True)
            enriched_df = pd.concat([enriched_df, fuzzy_df], ignore_index=True)
        # dropping duplicate songs ( wih the help of the id ) to reset the index    
        return enriched_df.drop_duplicates(subset='id').reset_index(drop=True)


# closest ( already made ) playlist based on tempo
def closest_playlist(spotify_df, user_df):
    # the average tempo of the user's playlist
    user_avg_tempo = user_df["tempo"].mean()
    # filter out any rows that don't have a valid playlist name ( incomplete data )
    valid_playlists = spotify_df.dropna(subset=["playlist_name"])
    # roup the remaining data by playlist name
    grouped = valid_playlists.groupby("playlist_name")
    # gives list of all available playlist names
    playlist_names = list(grouped.groups.keys())
    # finds the playlist whose average tempo is closest to the user's average tempo
    closest_name = min(
        playlist_names,
        key=lambda x: abs(grouped.get_group(x)["tempo"].mean() - user_avg_tempo)
    )
    # full playlist that was identified as the closest match
    return grouped.get_group(closest_name)

# playlist based on tempo & ranking so there's more variety in options
def generate_custom_playlist(sptfy_df, user_df, playlist_size=10):
    # get the user's average tempo ( bpm )
    user_avg_tempo = user_df['tempo'].mean()
    # to keep a musical vibe or feel, since the tempo affects the energy or rhythm, +/- of 15 bpm keeps the recs somewhat close in pace so that they're not completely too slow, different or too fast.
    # too narrow tempos, ex. +/- 5 bpm only would give almost identical songs without variety, whereas too wige, ex. +/- 40 would allow songs to be filtered & shown but could have a totally slow/fast, or even unrelated sort of tempo / "vibe" 
    tempo_range = (user_avg_tempo - 15, user_avg_tempo + 15)
    excluded_ids = set(user_df['id'])
    candidates = sptfy_df[
        sptfy_df['tempo'].between(*tempo_range) &
        ~sptfy_df['id'].isin(excluded_ids)
    ]
    # this is where popularity comes into play — from all the filtered possibilities, it will show them from most to least popular based already on the rempo 
    # overall, it will give not just familiar songs but also better discovery of potential songs you might like given your tempo average
    return candidates.sort_values(by='popularity', ascending=False).head(playlist_size)

# playlists based on other features
def generate_playlist_by_feature(sptfy_df, user_df, feature, playlist_size=10):
    # validation that the chosen feature exists in both datasets
    if feature not in sptfy_df.columns or feature not in user_df.columns:
        raise ValueError(f"Feature '{feature}' not found in data.")
    # calculates the average value of the selected feature from the user's playlist
    avg_feature = user_df[feature].mean()
    # fins difference between each song's feature value and the user's average
    sptfy_df['diff'] = (sptfy_df[feature] - avg_feature).abs()
    # sort songs by how close their feature value is to the user's average
    # also drops any duplicate songs by id & selects the top 10 closest matches
    recommended_df = sptfy_df.sort_values('diff').drop_duplicates(subset=['id']).head(playlist_size)
    recommended_df = recommended_df.drop(columns='diff')
    # result of only the relevant columns: id, name, artist, and the selected feature
    return recommended_df[['id', 'name', 'artists', feature]]


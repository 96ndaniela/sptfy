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
    if not all(col in user_df.columns for col in ['Id', 'Song', 'Artist']):
        raise KeyError("user playlist must contain 'Id', 'Song', 'Artist' columns.")
    # normalize column names
    user_df = user_df.rename(columns={'Id': 'id', 'Song': 'name', 'Artist': 'artists'})
    # merge by id first
    merged = pd.merge(user_df, spotify_df, on='id', how='left', suffixes=('_user', ''))

    # find entries missing any key audio features
    missing_data = merged[merged[FEATURE_COLUMNS].isnull().any(axis=1)]

    enriched_rows = []
    if not missing_data.empty:
        enriched_rows = []
        for _, user_row in missing_data.iterrows():
            best_match = None
            best_score = 0
            for _, spot_row in spotify_df.iterrows():
                score_name = fuzz.partial_ratio(user_row['name'], spot_row['name'])
                score_artist = fuzz.partial_ratio(user_row['artists'], spot_row['artists'])
                total_score = (score_name + score_artist) / 2
                if total_score > best_score and total_score > 85:
                    best_match = spot_row
                    best_score = total_score
            if best_match is not None:
                enriched_rows.append(pd.DataFrame([best_match]))
    # combine valid original matches and fuzzy matches
        enriched_df = merged.dropna(subset=FEATURE_COLUMNS)
        if enriched_rows:
            fuzzy_df = pd.concat(enriched_rows, ignore_index=True)
            enriched_df = pd.concat([enriched_df, fuzzy_df], ignore_index=True)
        return enriched_df.drop_duplicates(subset='id').reset_index(drop=True)


# closest ( already made ) playlist based on tempo
def closest_playlist(spotify_df, user_df):
    user_avg_tempo = user_df["tempo"].mean()
    valid_playlists = spotify_df.dropna(subset=["playlist_name"])
    grouped = valid_playlists.groupby("playlist_name")
    playlist_names = list(grouped.groups.keys())
    closest_name = min(
        playlist_names,
        key=lambda x: abs(grouped.get_group(x)["tempo"].mean() - user_avg_tempo)
    )

    return grouped.get_group(closest_name)

# playlist based on tempo & ranking so there's more variety in options
def generate_custom_playlist(sptfy_df, user_df, playlist_size=10):
    user_avg_tempo = user_df['tempo'].mean()
    tempo_range = (user_avg_tempo - 15, user_avg_tempo + 15)
    excluded_ids = set(user_df['id'])

    candidates = sptfy_df[
        sptfy_df['tempo'].between(*tempo_range) &
        ~sptfy_df['id'].isin(excluded_ids)
    ]
    return candidates.sort_values(by='popularity', ascending=False).head(playlist_size)

# playlists based on other features
def generate_playlist_by_feature(sptfy_df, user_df, feature, playlist_size=10):
    if feature not in sptfy_df.columns or feature not in user_df.columns:
        raise ValueError(f"Feature '{feature}' not found in data.")
    
    avg_feature = user_df[feature].mean()
    sptfy_df['diff'] = (sptfy_df[feature] - avg_feature).abs()
    recommended_df = sptfy_df.sort_values('diff').drop_duplicates(subset=['id']).head(playlist_size)
    recommended_df = recommended_df.drop(columns='diff')
    return recommended_df[['id', 'name', 'artists', feature]]


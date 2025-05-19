import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz

def load_sptfy(filepath, playlist_with=10):
    df = pd.read_csv(filepath)
 
    rename_map = {}
    if 'track_name' in df.columns:
        rename_map['track_name'] = 'name'
    if 'track_artist' in df.columns:
        rename_map['track_artist'] = 'artists'
    if 'track_popularity' in df.columns:
        rename_map['track_popularity'] = 'popularity'
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    required_cols = ['Id', 'name', 'artists', 'tempo', 'popularity']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"missing columns in spotify csv: {missing}")

    df = df.drop_duplicates(subset=['Id'])
    df = df.dropna(subset=['tempo', 'popularity'])
    df = df.reset_index(drop=True)

    if 'playlist_name' not in df.columns:
        n = len(df)
        df['playlist_name'] = [f"playlist_{(i // playlist_with) + 1}" for i in range(n)]

    return df

def enrich_user_playlist(user_df, sptfy_df):
    user_df = user_df.rename(columns={"Song": "name", "Artist": "artists"})

    if 'Id' not in user_df.columns:
        raise KeyError("User playlist must contain 'Id' column for matching.")

    matched_df = pd.merge(user_df, sptfy_df, on="Id", how="left", suffixes=('', '_spotify'))

    # fuzzy matching 
    unmatched = matched_df[matched_df['tempo'].isnull()]
    if not unmatched.empty:
        spotify_lookup = sptfy_df[['Id', 'name', 'artists']].copy()
        spotify_lookup['key'] = spotify_lookup['name'].str.lower() + ' - ' + spotify_lookup['artists'].str.lower()

        for idx, row in unmatched.iterrows():
            user_key = f"{str(row['name']).lower()} - {str(row['artists']).lower()}"
            match, score, match_idx = process.extractOne(
                user_key,
                spotify_lookup['key'],
                scorer=fuzz.token_sort_ratio
            )
            if score > 80:
                matched_id = spotify_lookup.iloc[match_idx]['Id']
                sptfy_row = sptfy_df[sptfy_df['Id'] == matched_id].iloc[0]
                for col in ['tempo', 'popularity', 'playlist_name']:
                    matched_df.at[idx, col] = sptfy_row[col]

    enriched_df = matched_df.dropna(subset=['tempo']).reset_index(drop=True)
    return enriched_df

def closest_playlist(sptfy_df, user_df):
    user_avg_tempo = user_df['tempo'].mean()
    grouped = sptfy_df.groupby('playlist_name')

    min_diff = float('inf')
    closest_name = None

    for playlist_name, group in grouped:
        avg_tempo = group['tempo'].mean()
        diff = abs(avg_tempo - user_avg_tempo)
        if diff < min_diff:
            min_diff = diff
            closest_name = playlist_name

    closest_df = sptfy_df[sptfy_df['playlist_name'] == closest_name]
    return closest_df.reset_index(drop=True)

def generate_custom_playlist(sptfy_df, user_df, exclude_ids=None, size=10):
    if exclude_ids is None:
        exclude_ids = []

    user_avg_tempo = user_df['tempo'].mean()
    tempo_range = (user_avg_tempo - 15, user_avg_tempo + 15)

    filtered = sptfy_df[
        (sptfy_df['tempo'] >= tempo_range[0]) &
        (sptfy_df['tempo'] <= tempo_range[1]) &
        (~sptfy_df['Id'].isin(exclude_ids))
    ]

    filtered = filtered.sort_values(by='popularity', ascending=False)
    return filtered.head(size).reset_index(drop=True)

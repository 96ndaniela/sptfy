import pandas as pd
import numpy as np
from rapidfuzz import fuzz

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
        raise KeyError("User playlist must contain 'Id', 'Song', 'Artist' columns.")

    user_df = user_df.rename(columns={'Id': 'id', 'Song': 'name', 'Artist': 'artists'})

    merged = pd.merge(user_df, spotify_df, on='id', how='left', suffixes=('_user', ''))

     missing_data = merged[merged['tempo'].isna()]
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

        if enriched_rows:
            enriched_df = pd.concat([merged.dropna(subset=['tempo'])] + enriched_rows, ignore_index=True)
            return enriched_df.drop_duplicates(subset='id')
    return merged.dropna(subset=['tempo'])

def closest_playlist(sptfy_df, user_df):
    user_avg_tempo = user_df['tempo'].mean()
    grouped = sptfy_df.groupby('playlist_name')

    closest_name = min(
        grouped,
        key=lambda x: abs(grouped.get_group(x)['tempo'].mean() - user_avg_tempo)
    )
    return sptfy_df[sptfy_df['playlist_name'] == closest_name]

def generate_custom_playlist(sptfy_df, user_df, playlist_size=10):
    user_avg_tempo = user_df['tempo'].mean()
    tempo_range = (user_avg_tempo - 15, user_avg_tempo + 15)
    excluded_ids = set(user_df['id'])

    candidates = sptfy_df[
        sptfy_df['tempo'].between(*tempo_range) &
        ~sptfy_df['id'].isin(excluded_ids)
    ]
    return candidates.sort_values(by='popularity', ascending=False).head(playlist_size)

import pandas as pd
import numpy as np

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

    required_cols = ['name', 'artists', 'tempo', 'popularity']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"missing columns in spotify dataset: {missing}")

    df = df.drop_duplicates(subset=['name', 'artists'])
    df = df.dropna(subset=['tempo', 'popularity'])
    df = df.reset_index(drop=True)

    if 'playlist_name' not in df.columns:
        n = len(df)
        playlist_new = [f"playlist_{(i // playlist_with) + 1}" for i in range(n)]
        df['playlist_name'] = playlist_new

    return df

def enrich_user_playlist(user_df, sptfy_df):
    original_cols = user_df.columns.tolist()
    rename_map = {}

    if 'track_name' in user_df.columns:
        rename_map['track_name'] = 'name'
    if 'track_artist' in user_df.columns:
        rename_map['track_artist'] = 'artists'
    if 'track_popularity' in user_df.columns:
        rename_map['track_popularity'] = 'popularity'

    user_df = user_df.rename(columns=rename_map)

    #  
    if 'name' not in user_df.columns or 'artists' not in user_df.columns:
        raise KeyError(
            f"your playlist file must contain either columns ['name', 'artists'] or ['track_name', 'track_artist'].\n"
            f"found columns: {original_cols}"
        )

    enriched_df = pd.merge(
        user_df,
        sptfy_df[['name', 'artists', 'tempo', 'popularity']],
        on=['name', 'artists'],
        how='left'
    )

    enriched_df = enriched_df.dropna(subset=['tempo'])
    return enriched_df

def match_usersongs(sptfy_df, user_df):
    user_avg_tempo = user_df['tempo'].mean()
    grouped = sptfy_df.groupby('playlist_name')

    min_diff = float('inf')
    closest_playlist_name = None

    for playlist_name, group in grouped:
        avg_tempo = group['tempo'].mean()
        diff = abs(avg_tempo - user_avg_tempo)
        if diff < min_diff:
            min_diff = diff
            closest_playlist_name = playlist_name

    if closest_playlist_name is None:
        raise ValueError("No similar playlist found.")

    return sptfy_df[sptfy_df['playlist_name'] == closest_playlist_name].reset_index(drop=True)

def generate_custom_playlist(sptfy_df, user_tracks_df, exclude_tracks=None, playlist_size=10):
    if exclude_tracks is None:
        exclude_tracks = []

    user_avg_tempo = user_tracks_df['tempo'].mean()
    tempo_lower = user_avg_tempo - 15
    tempo_upper = user_avg_tempo + 15

    filtered = sptfy_df[
        (sptfy_df['tempo'] >= tempo_lower) &
        (sptfy_df['tempo'] <= tempo_upper) &
        (~sptfy_df['name'].isin(exclude_tracks))
    ]

    filtered = filtered.sort_values(by='popularity', ascending=False)
    return filtered.head(playlist_size).reset_index(drop=True)

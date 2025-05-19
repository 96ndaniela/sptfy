import pandas as pd
import numpy as np

def load_sptfy(filepath, playlist_with=10):
    df = pd.read_csv(filepath)

    # rename columns 
    df.rename(columns={
        'track_name': 'name',
        'track_artist': 'artists',
        'track_popularity': 'popularity'
    }, inplace=True)

    required_cols = ['name', 'artists', 'tempo', 'popularity']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"missing columns in csv: {missing}")

    df = df.drop_duplicates(subset=['name', 'artists'])
    df = df.dropna(subset=['tempo', 'popularity'])
    df = df.reset_index(drop=True)

    if 'playlist_name' not in df.columns:
        n = len(df)
        playlist_new = []
        for i in range(n):
            playlist_num = (i // playlist_with) + 1
            playlist_new.append(f"playlist_{playlist_num}")
        df['playlist_name'] = playlist_new

    return df

def match_usersongs(sptfy_df, uplay_datafr):
    uplay_datafr.rename(columns={
        'track_name': 'name',
        'track_artist': 'artists'
    }, inplace=True)

    merged = pd.merge(uplay_datafr, sptfy_df, on=['name', 'artists'], how='inner', suffixes=('_user', '_spotify'))
    if merged.empty:
        merged = pd.merge(uplay_datafr, sptfy_df, on=['name'], how='inner', suffixes=('_user', '_spotify'))
    cols = sptfy_df.columns.tolist()
    return merged[cols]

def closest_playlist(sptfy_df, utracks_df):
    user_avg_tempo = utracks_df['tempo'].mean()
    grouped = sptfy_df.groupby('playlist_name')

    min_diff = float('inf')
    closest_playlist_name = None

    for playlist_name, group in grouped:
        avg_tempo = group['tempo'].mean()
        diff = abs(avg_tempo - user_avg_tempo)
        if diff < min_diff:
            min_diff = diff
            closest_playlist_name = playlist_name

    closest_playlist_df = sptfy_df[sptfy_df['playlist_name'] == closest_playlist_name]
    return closest_playlist_df.reset_index(drop=True), closest_playlist_df

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
    new_playlist = filtered.head(playlist_size).reset_index(drop=True)

    return new_playlist

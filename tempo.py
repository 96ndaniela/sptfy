import pandas as pd
import numpy as np
import streamlit as st  

def load_sptfy(filepath, playlist_with=10):
    df = pd.read_csv(filepath)

    # rename columns if they exist
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
        raise ValueError(f"missing columns in csv: {missing}")

    df = df.drop_duplicates(subset=['name', 'artists'])
    df = df.dropna(subset=['tempo', 'popularity'])
    df = df.reset_index(drop=True)

    if 'playlist_name' not in df.columns:
        n = len(df)
        playlist_new = [f"playlist_{(i // playlist_with) + 1}" for i in range(n)]
        df['playlist_name'] = playlist_new

    return df

def match_usersongs(sptfy_df, uplay_datafr):
    # rename columns in user dataframe if needed
    rename_map = {}
    if 'track_name' in uplay_datafr.columns and 'name' not in uplay_datafr.columns:
        rename_map['track_name'] = 'name'
    if 'track_artist' in uplay_datafr.columns and 'artists' not in uplay_datafr.columns:
        rename_map['track_artist'] = 'artists'
    if rename_map:
        uplay_datafr = uplay_datafr.rename(columns=rename_map)

    # columns existence before merge
    merge_cols = ['name', 'artists']
    missing_in_user = [col for col in merge_cols if col not in uplay_datafr.columns]
    missing_in_sptfy = [col for col in merge_cols if col not in sptfy_df.columns]

    if missing_in_user or missing_in_sptfy:
        st.error(f"Missing columns for merge:\n - User DF missing: {missing_in_user}\n - Spotify DF missing: {missing_in_sptfy}")
        #  empty DataFrame with same columns as sptfy_df to avoid breaking 
        return pd.DataFrame(columns=sptfy_df.columns)

    # try merge on both columns
    merged = pd.merge(uplay_datafr, sptfy_df, on=merge_cols, how='inner', suffixes=('_user', '_spotify'))

    # try merge on just 'name' if possible
    if merged.empty and 'name' in uplay_datafr.columns and 'name' in sptfy_df.columns:
        merged = pd.merge(uplay_datafr, sptfy_df, on=['name'], how='inner', suffixes=('_user', '_spotify'))

    if merged.empty:
        st.warning("No matching songs found between user data and Spotify data.")

    # return only columns from spotify dataframe  
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

import pandas as pd
from rapidfuzz import process, fuzz

def load_sptfy(filepath, playlist_with=10):
    df = pd.read_csv(filepath)

    #  uniformity
    rename_map = {
        'track_id': 'Id',
        'track_name': 'name',
        'track_artist': 'artists',
        'track_popularity': 'popularity',
        'playlist_name': 'playlist_name',
        'tempo': 'tempo'
    }
    df = df.rename(columns=rename_map)

    #   needed columns (add others if needed)
    needed_cols = ['Id', 'name', 'artists', 'popularity', 'playlist_name', 'tempo']
    df = df[needed_cols].drop_duplicates(subset=['Id'])

    #  create dummy playlists
    if 'playlist_name' not in df.columns or df['playlist_name'].isnull().all():
        n = len(df)
        df['playlist_name'] = [f"playlist_{(i // playlist_with) + 1}" for i in range(n)]

    return df

def enrich_user_playlist(user_df, sptfy_df):
    # rename  for uniformity
    user_df = user_df.rename(columns={"Song": "name", "Artist": "artists", "Id": "Id"})

    # merge on id if possible
    if 'Id' in user_df.columns and user_df['Id'].notnull().all():
        matched_df = pd.merge(user_df, sptfy_df, on='Id', how='left', suffixes=('', '_spotify'))
        matched_df = matched_df[['Id', 'name_x', 'artists_x', 'tempo', 'popularity', 'playlist_name']]
        matched_df.rename(columns={'name_x': 'name', 'artists_x': 'artists'}, inplace=True)
        missing_tempo = matched_df['tempo'].isnull()
        if missing_tempo.any():
            missing_rows = matched_df[missing_tempo]
            fuzzy_enriched = fuzzy_match_enrichment(missing_rows[['name', 'artists']], sptfy_df)
            matched_df.loc[missing_tempo, ['tempo', 'popularity', 'playlist_name']] = fuzzy_enriched[['tempo', 'popularity', 'playlist_name']].values
    else:
        matched_df = fuzzy_match_enrichment(user_df[['name', 'artists']], sptfy_df)

    matched_df = matched_df.dropna(subset=['tempo']).reset_index(drop=True)
    return matched_df

def fuzzy_match_enrichment(user_subset_df, sptfy_df):
    # keys for matching
    user_subset_df = user_subset_df.copy()
    sptfy_df = sptfy_df.copy()

    user_subset_df['key'] = (user_subset_df['name'].str.lower().fillna('') + ' - ' + user_subset_df['artists'].str.lower().fillna('')).str.strip()
    sptfy_df['key'] = (sptfy_df['name'].str.lower().fillna('') + ' - ' + sptfy_df['artists'].str.lower().fillna('')).str.strip()

    enriched_rows = []
    for idx, row in user_subset_df.iterrows():
        user_key = row['key']
        match, score, match_idx = process.extractOne(
            user_key,
            sptfy_df['key'],
            scorer=fuzz.token_sort_ratio
        )
        if score > 80:
            matched_row = sptfy_df.iloc[match_idx]
            enriched_row = row.to_dict()
            for col in ['tempo', 'popularity', 'playlist_name', 'Id']:
                enriched_row[col] = matched_row[col]
            enriched_rows.append(enriched_row)
        else:
            enriched_rows.append({**row.to_dict(), 'tempo': None, 'popularity': None, 'playlist_name': None, 'Id': None})

    return pd.DataFrame(enriched_rows)

def closest_playlist(sptfy_df, user_tracks_df):
    user_avg_tempo = user_tracks_df['tempo'].mean()
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
    return closest_playlist_df.reset_index(drop=True)

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

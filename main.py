import sys
import os 

# confirm the current file directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import custom functions from tempo.py ( functions that will be used for creating, and showing current playlists )
from tempo import (
    load_sptfy, 
    enrich_user_playlist, 
    closest_playlist, 
    generate_custom_playlist,
    generate_playlist_by_feature
)
# streamlit page layout configuration
st.set_page_config(page_title="spotify song recommendations", layout="wide")

@st.cache_data
def load_data():
    """
    loads the main spotify dataset and predefined user playlists that have been giving for the challenge: user a, b, j & o, 
    and the spotify dataset with robust information of each song listed.

    returns:
        sptfy_df ( dataframe ): main spotify dataset
        user_files ( list ): user playlist file paths.
    """
    sptfy_df = load_sptfy("data/spotify_songs.csv")
    user_files = {
        "User A": "data/User_A.csv",
        "User B": "data/User_B.csv",
        "User J": "data/User_J.csv",
        "User O": "data/User_O.csv",
    }
    return sptfy_df, user_files

def plot_tempo_distribution(df, title):
# plots a histogram of song tempos with the given playlist's data and the title itself for the page
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df["tempo"], kde=True, ax=ax, color='skyblue')
    ax.set_title(title)
    ax.set_xlabel("tempo")
    ax.set_ylabel("frequency")
    st.pyplot(fig)

def plot_popularity_bar(df, title):
    top_songs = df.sort_values(by="popularity", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="popularity", y="name", data=top_songs, ax=ax, palette="viridis")
    ax.set_title(title)
    st.pyplot(fig)

def main():
    st.title("spotify song recommendations")

    sptfy_df, user_files = load_data()
    st.sidebar.header("choose a playlist")
    user_choice = st.sidebar.selectbox("user:", list(user_files.keys()) + ["upload new"])

    if user_choice == "upload new":
        uploaded_file = st.sidebar.file_uploader("upload a new csv playlist", type=["csv"])
        if uploaded_file is None:
            st.warning("please upload a file.")
            st.stop()
        raw_user_df = pd.read_csv(uploaded_file)
        user_name = "uploaded user"
    else:
        raw_user_df = pd.read_csv(user_files[user_choice])
        user_name = user_choice
    user_df = None
    try:
    # add needed or wanted information to the uploaded playlists with metadata from spotify dataset. 
        user_df = enrich_user_playlist(raw_user_df, sptfy_df)
    # sptfy id + the id shown in the csv must match
        if user_df.empty: 
            st.warning("no matching songs found in the spotify dataset.") 
    except Exception as e:
            st.error(f"failed to process playlist: {e}")
            st.stop()
        
    # displays original playlist ( no modifications have been made, therefore showing what the csv has )
    st.subheader(f"original playlist for {user_name}")
    st.dataframe(user_df[['name', 'artists', 'tempo', 'popularity']])
    
    # shows tempo distribution of user playlist
    st.subheader("playlist's tempo")
    plot_tempo_distribution(user_df, "your playlist's tempo distribution")
    
    # shows tempo distribution of user playlist
    st.subheader("top songs recommendations")
    plot_popularity_bar(user_df, "most popular songs")

    # shows closest matching playlist from the dataset, taking the information from "playlist_name" based on tempo's average 
    existing_playlist_df = closest_playlist(sptfy_df, user_df)
    st.subheader("closest playlist")
    st.dataframe(existing_playlist_df[['name', 'artists', 'playlist_name', 'tempo', 'popularity']].head(10))
    
    # creates a new playlist based on tempo and popularity of the user's song choices, so it matches closely to their original's tempo and shows the most popular ones that would match
    generated_playlist = generate_custom_playlist(sptfy_df, user_df)
    st.subheader("custom new playlist")
    st.dataframe(generated_playlist[['name', 'artists', 'tempo', 'popularity']])

    st.success("recommendations generated using tempo and popularity.")

    # other available features
    st.sidebar.header("other features")
    features = [
        'danceability', 'energy', 'key', 'loudness', 'mode',
        'speechiness', 'acousticness', 'liveness'
    ]
    selected_feature = st.sidebar.selectbox("choose a feature for recommendation:", features)
    generate_btn = st.sidebar.button("generate feature-based playlist")

    if generate_btn:
        st.subheader(f"custom playlist based on '{selected_feature}'")
        try:
            feature_playlist = generate_playlist_by_feature(sptfy_df, user_df, feature=selected_feature)
            columns_to_show = [col for col in feature_playlist.columns if col != 'id']
            st.dataframe(feature_playlist)
            st.success(f"recommendations generated using '{selected_feature}'.")
        except Exception as e:
            st.error(f"could not generate recommendations using '{selected_feature}': {e}")


if __name__ == "__main__":
    main()

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tempo import load_sptfy, enrich_user_playlist, closest_playlist, generate_custom_playlist

st.set_page_config(page_title="test", layout="wide")

@st.cache_data
def load_data():
    sptfy_df = load_sptfy("data/spotify_songs.csv")
    user_files = {
        "User A": "data/User_A.csv",
        "User B": "data/User_B.csv",
        "User J": "data/User_J.csv",
        "User O": "data/User_O.csv",
    }
    return sptfy_df, user_files

def plot_tempo_distribution(df, title):
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
    st.title("test")

    sptfy_df, user_files = load_data()
    st.sidebar.header("Choose or Upload a Playlist")
    user_choice = st.sidebar.selectbox("Select User:", list(user_files.keys()) + ["upload new"])

    if user_choice == "upload new":
        uploaded_file = st.sidebar.file_uploader("uploada csv", type=["csv"])
        if uploaded_file is None:
            st.warning("Please upload a file.")
            st.stop()
        raw_user_df = pd.read_csv(uploaded_file)
        user_name = "uploaded user"
    else:
        raw_user_df = pd.read_csv(user_files[user_choice])
        user_name = user_choice

    try:
        user_df = enrich_user_playlist(raw_user_df, sptfy_df)
    except Exception as e:
        st.error(f"failed to process playlist: {e}")
        st.stop()

    if user_df.empty:
        st.warning("no matching songs found in the spotify dataset.") 

    st.subheader(f"original playlist for {user_name}")
    st.dataframe(user_df[['name', 'artists', 'tempo', 'popularity']])

    st.subheader("tempo")
    plot_tempo_distribution(user_df, "your playlist tempo distribution")

    st.subheader("top songs")
    plot_popularity_bar(user_df, "Most Popular Songs")

    existing_playlist_df = closest_playlist(sptfy_df, user_df)
    st.subheader("closest ")
    st.dataframe(existing_playlist_df[['name', 'artists', 'playlist_name', 'tempo', 'popularity']].head(10))

    generated_playlist = generate_custom_playlist(sptfy_df, user_df)
    st.subheader("custom  ")
    st.dataframe(generated_playlist[['name', 'artists', 'tempo', 'popularity']])

    st.success("recommendations generated using tempo and popularity.")

if __name__ == "__main__":
    main()

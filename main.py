import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
 

st.set_page_config(page_title="spotify recommendations", layout="wide")

@st.cache_data
def load_data():
    spotify_df = load_sptfy("data/spotify_songs.csv", playlist_with=10)
    user_files = {
        "User A": "data/User_A.csv",
        "User B": "data/User_B.csv",
        "User J": "data/User_J.csv",
        "User O": "data/User_O.csv",
    }
    return spotify_df, user_files

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
    st.title("spotify recommendations based on tempo & popularity")

    sptfy_df, user_files = load_data()
    st.sidebar.header("choose or upload a playlist")
    user_choice = st.sidebar.selectbox("select user:", list(user_files.keys()) + ["upload new"])

    if user_choice == "upload new":
        uploaded_file = st.sidebar.file_uploader("upload your playlist in csv format", type=["csv"])
        if uploaded_file is not None:
            user_df = pd.read_csv(uploaded_file)
            user_name = "new user uploaded"
        else:
            st.info("please upload a new csv file to continue.")
            st.stop()
    else:
        user_name = user_choice
        user_df = pd.read_csv(user_files[user_choice])

    st.subheader(f"original playlist for {user_name}")
    st.dataframe(user_df.head(10))

    matched_user_df = match_usersongs(sptfy_df, user_df)
    if matched_user_df.empty:
        st.warning("no matching songs found in the spotify dataset.")
        st.stop()

    st.subheader("tempo distribution of your playlist")
    plot_tempo_distribution(matched_user_df, "your playlist tempo distribution")

    st.subheader("top songs by popularity")
    plot_popularity_bar(matched_user_df, "most popular songs")

    #closest
    closest_df, closest_name = closest_playlist(sptfy_df, matched_user_df)
    st.subheader(f"recommendation from existing playlist: {closest_name}")
    st.dataframe(closest_df[["name", "artists", "playlist_name", "tempo", "popularity"]])

    #new custom playlist
    exclude = matched_user_df['name'].tolist()
    custom_playlist = generate_custom_playlist(sptfy_df, matched_user_df, exclude_tracks=exclude)
    st.subheader("new playlist created for you")
    st.dataframe(custom_playlist[["name", "artists", "tempo", "popularity"]])

    st.success("these recommendations were generated using tempo similarity + popularity filtering.")

if __name__ == "__main__":
    main()

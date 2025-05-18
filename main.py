import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.tempo import ( 
)

st.set_page_config(page_title="spotify recommendations", layout="wide")

@st.cache_data
def load_data():
    spotify_df = load_spotify_data("data/spotify_songs.csv")
    user_files = {
        "User A": "data/User_A.csv",
        "User B": "data/User_B.csv",
        "User J": "data/User_J.csv",
        "User O": "data/User_O.csv",
    }
    return spotify_df, user_files

def main():
    st.title("spotify: song recommendations (based on tempo & ranking")
    sptfy_df, user_files = load_data()

    st.sidebar.header("select user, or upload a new csv")
    user_choice = st.sidebar.selectbox("choose an user playlist:", list(user_files.keys()) + ["upload new"])

    if user_choice == "upload new":
        uploaded_file = st.sidebar.file_uploader("upload your playlist in csv form", type=["csv"])
        if uploaded_file is not None:
            user_df = pd.read_csv(uploaded_file)
            user_name = "new user uploaded!"
        else:
            st.info("please upload a new csv.")
            st.stop()
    else:
        user_name = user_choice
        user_df = pd.read_csv(user_files[user_choice])

if __name__ == "__main__":
    main()

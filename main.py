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

if __name__ == "__main__":
    main()

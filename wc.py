import io
import json
import os
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="The Walker Cup 2026", page_icon="⛳", layout="centered"
)

SAVE_FILE = "wc_scores_backup.json"

# --- PLAYER DATA & INITIALS ---
PLAYERS = {"Scott": 17.3, "Troy": 24.1, "Allen": 28.2}
INITIALS = {"Scott": "SCW", "Troy": "TAC", "Allen": "ATN"}

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15
}

# --- COURSE DEFINITIONS WITH OFFICIAL SCORECARDS ---
COURSES = {
    "Salt Pond (Black Tees)": {
        "rating": 56.5,
        "slope": 96,
        "par": 61,

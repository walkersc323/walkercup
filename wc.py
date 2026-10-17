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
        "holes": [
            {"num": 1, "par": 3, "hcp": 6, "yds": 151, "tips": {"Scott": "Career avg 4.50—smooth iron to center green.", "Troy": "Career avg 3.50—stroke hole, aim at flag.", "Allen": "Career avg 7.00—stroke hole, take extra club off tee."}},
            {"num": 2, "par": 3, "hcp": 18, "yds": 113, "tips": {"Scott": "Career avg 3.50—short iron in hand; attack flag.", "Troy": "Career avg 3.00—high par rate; trust distance.", "Allen": "Career avg 4.00—easiest handicap rank, go for pin."}},
            {"num": 3, "par": 3, "hcp": 8, "yds": 180, "tips": {"Scott": "Career avg 4.00—6-point tier, favor center green.", "Troy": "Career avg 3.00—stroke hole, high point yield.", "Allen": "Career avg 4.00—stroke hole, play middle green."}},
            {"num": 4, "par": 3, "hcp": 16, "yds": 104, "tips": {"Scott": "Career avg 3.00—YOUR BEST PAR 3! Attack pin.", "Troy": "Career avg 3.00—wedge range, attack pin directly.", "Allen": "Career avg 4.00—smooth swing to green center."}},
            {"num": 5, "par": 4, "hcp": 2, "yds": 260, "tips": {"Scott": "Career avg 4.00—only par 4 on front; 9-point tier.", "Troy": "Career avg 4.50—stroke hole, keep drive in fairway.", "Allen": "Career avg 5.00—stroke hole, play for net par."}},
            {"num": 6, "par": 3, "hcp": 14, "yds": 150, "tips": {"Scott": "Career avg 4.00—favor green center.", "Troy": "Career avg 4.00—solid par history.", "Allen": "Career avg 3.00—GREAT PAR HOLE FOR YOU!"}},
            {"num": 7, "par": 3, "hcp": 10, "yds": 200, "tips": {"Scott": "Career avg 3.50—check wind off trees; long par 3.", "Troy": "Career avg 4.00—stroke hole, aim center.", "Allen": "Career avg 6.00—stroke hole, club up."}},
            {"num": 8, "par": 3, "hcp": 4, "yds": 184, "tips": {"Scott": "Career avg 4.50—9-point tier, favor front green.", "Troy": "Career avg 3.50—stroke hole, aggressive birdie chance.", "Allen": "Career avg 4.00—stroke hole, great net score history."}},
            {"num": 9, "par": 3, "hcp": 12, "yds": 125, "tips": {"Scott": "Career avg 4.00—solid front finish.", "Troy": "Career avg 5.00—watch front bunker.", "Allen": "Career avg 4.00—smooth swing to middle green."}},
            {"num": 10, "par": 3, "hcp": 7, "yds": 177, "tips": {"Scott": "Career avg 4.00—back 9 opener; 6-point tier.", "Troy": "Career avg 3.50—stroke hole, great start to back 9.", "Allen": "Career avg 4.00—stroke hole, solid par setup."}},
            {"num": 11, "par": 3, "hcp": 17, "yds": 112, "tips": {"Scott": "Career avg 4.00—short hole; attack pin location.", "Troy": "Career avg 4.00—high par conversion rate.", "Allen": "Career avg 3.00—EXCELLENT SCORING HOLE!"}},
            {"num": 12, "par": 3, "hcp": 5, "yds": 198, "tips": {"Scott": "Career avg 3.00—9-point tier, long iron test.", "Troy": "Career avg 2.50—stroke hole, YOUR BEST HOLE AT SALT POND!", "Allen": "Career avg 3.00—stroke hole, net birdie candidate!"}},
            {"num": 13, "par": 3, "hcp": 11, "yds": 212, "tips": {"Scott": "Career avg 3.50—longest par 3 on back 9.", "Troy": "Career avg 3.00—stroke hole, high point yield.", "Allen": "Career avg 3.00—stroke hole, favor center green."}},
            {"num": 14, "par": 3, "hcp": 13, "yds": 165, "tips": {"Scott": "Career avg 4.50—mid-iron approach.", "Troy": "Career avg 3.50—aggressive tee shot path.", "Allen": "Career avg 5.00—play safe layup/chip."}},
            {"num": 15, "par": 3, "hcp": 15, "yds": 143, "tips": {"Scott": "Career avg 3.00—high par conversion hole.", "Troy": "Career avg 3.00—attack flag directly.", "Allen": "Career avg 3.00—great par performance."}},
            {"num": 16, "par": 4, "hcp": 1, "yds": 260, "tips": {"Scott": "Career avg 5.00—HCP #1, 9-point tier, drivable par 4.", "Troy": "Career avg 5.00—stroke hole, keep drive straight.", "Allen": "Career avg 4.00—stroke hole, play safe layup."}},
            {"num": 17, "par": 3, "hcp": 9, "yds": 170, "tips": {"Scott": "Career avg 5.00—penultimate par 3; 6-point tier.", "Troy": "Career avg 5.50—stroke hole, favor center green.", "Allen": "Career avg 4.00—stroke hole, net par candidate."}},
            {"num": 18, "par": 3, "hcp": 3, "yds": 190, "tips": {"Scott": "Career avg 4.50—closing hole; 9-point tier finish.", "Troy": "Career avg 6.00—stroke hole, finish strong.", "Allen": "Career avg 3.00—stroke hole, YOUR BEST CLOSING HOLE!"}},
        ],
    },

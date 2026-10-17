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

# --- COURSE DEFINITIONS WITH OFFICIAL SCORECARDS & HISTORICAL INSIGHTS ---
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
    "Baywood Greens (White Tees)": {
        "rating": 70.2,
        "slope": 134,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 13, "yds": 349, "tips": {"Scott": "Career avg 4.60—solid opener, favor left-center.", "Troy": "Career avg 4.20—great hole for you; be aggressive.", "Allen": "Career avg 6.00—stroke hole, play for net par."}},
            {"num": 2, "par": 4, "hcp": 11, "yds": 318, "tips": {"Scott": "Career avg 5.20—steady par/bogey history.", "Troy": "Career avg 4.60—stroke hole advantage, attack flag.", "Allen": "Career avg 6.75—stroke hole, play safe layup."}},
            {"num": 3, "par": 4, "hcp": 3, "yds": 395, "tips": {"Scott": "Career avg 5.80—9-point tier, guard against right hazard.", "Troy": "Career avg 5.00—stroke hole, solid par candidate.", "Allen": "Career avg 5.20—stroke hole, smooth tempo."}},
            {"num": 4, "par": 4, "hcp": 1, "yds": 422, "tips": {"Scott": "Career avg 7.20—HCP #1, 9-point tier, long approach over traps.", "Troy": "Career avg 5.40—stroke hole, you play this very well.", "Allen": "Career avg 6.50—stroke hole, play center green."}},
            {"num": 5, "par": 5, "hcp": 5, "yds": 515, "tips": {"Scott": "Career avg 8.00—9-point tier, play conservative layups.", "Troy": "Career avg 8.60—stroke hole, avoid water right at all costs.", "Allen": "Career avg 6.60—stroke hole, you score best here!"}},
            {"num": 6, "par": 3, "hcp": 15, "yds": 202, "tips": {"Scott": "Career avg 5.60—long par 3, take extra club.", "Troy": "Career avg 6.20—smooth swing into green center.", "Allen": "Career avg 5.20—great chance for net par."}},
            {"num": 7, "par": 5, "hcp": 7, "yds": 480, "tips": {"Scott": "Career avg 6.25—favor left side of fairway.", "Troy": "Career avg 7.00—stroke hole, use your handicap pad.", "Allen": "Career avg 7.40—stroke hole, play for smart bogey."}},
            {"num": 8, "par": 3, "hcp": 17, "yds": 131, "tips": {"Scott": "Career avg 3.25—YOUR BEST HOLE AT BAYWOOD! Attack flag.", "Troy": "Career avg 3.50—great historical scoring hole for you.", "Allen": "Career avg 4.20—high point yield hole for you."}},
            {"num": 9, "par": 4, "hcp": 9, "yds": 320, "tips": {"Scott": "Career avg 4.75—6-point tier, strong front finish history.", "Troy": "Career avg 4.75—stroke hole, play center green.", "Allen": "Career avg 6.40—stroke hole, take clean contact."}},
            {"num": 10, "par": 4, "hcp": 4, "yds": 360, "tips": {"Scott": "Career avg 5.75—9-point tier, good start to back nine.", "Troy": "Career avg 6.50—stroke hole, favor right fairway.", "Allen": "Career avg 7.00—stroke hole, keep drive in play."}},
            {"num": 11, "par": 3, "hcp": 16, "yds": 139, "tips": {"Scott": "Career avg 3.50—high par rate, attack flag directly.", "Troy": "Career avg 4.75—aim center green, avoid left trap.", "Allen": "Career avg 6.40—focus on smooth iron tempo."}},
            {"num": 12, "par": 4, "hcp": 18, "yds": 288, "tips": {"Scott": "Career avg 5.00—easiest HCP rank, short par 4, wedge in hand.", "Troy": "Career avg 5.00—great scoring opportunity.", "Allen": "Career avg 7.00—attack pin."}},
            {"num": 13, "par": 5, "hcp": 14, "yds": 477, "tips": {"Scott": "Career avg 6.75—tricky green slopes, aim below cup.", "Troy": "Career avg 6.75—favor left side.", "Allen": "Career avg 8.20—stroke hole, play safe bogey."}},
            {"num": 14, "par": 4, "hcp": 2, "yds": 385, "tips": {"Scott": "Career avg 6.50—HCP #2, 9-point tier, play for front green.", "Troy": "Career avg 5.25—stroke hole, high point yield.", "Allen": "Career avg 7.60—stroke hole, play center green."}},
            {"num": 15, "par": 3, "hcp": 12, "yds": 145, "tips": {"Scott": "Career avg 4.25—water left, favor right fringe.", "Troy": "Career avg 4.25—you score very well here; attack.", "Allen": "Career avg 3.50—YOUR BEST PAR 3 AT BAYWOOD!"}},
            {"num": 16, "par": 5, "hcp": 10, "yds": 452, "tips": {"Scott": "Career avg 6.25—6-point tier, reach in 3 clean shots.", "Troy": "Career avg 6.50—stroke hole, good scoring spot.", "Allen": "Career avg 7.25—stroke hole, keep drive in fairway."}},
            {"num": 17, "par": 4, "hcp": 8, "yds": 364, "tips": {"Scott": "Career avg 6.00—penultimate hole, watch right hazard.", "Troy": "Career avg 4.75—stroke hole, aggressive birdie path.", "Allen": "Career avg 6.75—stroke hole, play three clean shots."}},
            {"num": 18, "par": 4, "hcp": 6, "yds": 346, "tips": {"Scott": "Career avg 5.75—9-point tier finish, aim at clubhouse.", "Troy": "Career avg 6.00—stroke hole, finish strong.", "Allen": "Career avg 6.25—solid closing performance."}},
        ],
    },
    "Odessa National (Gold Tees)": {
        "rating": 66.9,
        "slope": 124,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 5, "yds": 343, "tips": {"Scott": "6-point tier—solid opener, favor center fairway.", "Troy": "Stroke hole—take advantage of your extra stroke.", "Allen": "Stroke hole—keep tee shot in play."}},
            {"num": 2, "par": 5, "hcp": 1, "yds": 536, "tips": {"Scott": "HCP #1 monster—9-point tier, play smart layups.", "Troy": "Stroke hole—avoid water/bunkers on left.", "Allen": "Stroke hole—you get a stroke; play for net par."}},
            {"num": 3, "par": 4, "hcp": 7, "yds": 324, "tips": {"Scott": "6-point tier—short par 4, wedge in hand.", "Troy": "Stroke hole—favor center green.", "Allen": "Stroke hole—smooth tempo off tee."}},
            {"num": 4, "par": 4, "hcp": 11, "yds": 276, "tips": {"Scott": "Drivable/short par 4—6-point tier, position over distance.", "Troy": "Stroke hole—great birdie/par opportunity.", "Allen": "Stroke hole—clean contact is priority."}},
            {"num": 5, "par": 5, "hcp": 13, "yds": 475, "tips": {"Scott": "Reachable in 3—play safe layup.", "Troy": "Solid par 5 scoring chance.", "Allen": "Stroke hole—good spot for net par."}},
            {"num": 6, "par": 3, "hcp": 17, "yds": 118, "tips": {"Scott": "Short iron in hand—attack pin location.", "Troy": "Easy iron distance—aim center green.", "Allen": "High point yield chance—trust club."}},
            {"num": 7, "par": 4, "hcp": 3, "yds": 302, "tips": {"Scott": "9-point tier—favor left-center fairway.", "Troy": "Stroke hole—take extra club on approach.", "Allen": "Stroke hole—play center green."}},
            {"num": 8, "par": 4, "hcp": 9, "yds": 335, "tips": {"Scott": "6-point tier—mid-handicap test, favor fairway.", "Troy": "Stroke hole—solid par candidate.", "Allen": "Stroke hole—keep drive in play."}},
            {"num": 9, "par": 3, "hcp": 15, "yds": 140, "tips": {"Scott": "Front nine finish—aim for green center.", "Troy": "Comfortable iron range.", "Allen": "Great net score history."}},
            {"num": 10, "par": 4, "hcp": 12, "yds": 342, "tips": {"Scott": "Back nine opener—6-point tier.", "Troy": "Stroke hole—favor right fairway.", "Allen": "Stroke hole—steady bogey/par."}},
            {"num": 11, "par": 5, "hcp": 6, "yds": 498, "tips": {"Scott": "9-point tier—three clean shots to green.", "Troy": "Stroke hole—aggressive birdie path.", "Allen": "Stroke hole—make up points here."}},
            {"num": 12, "par": 4, "hcp": 14, "yds": 298, "tips": {"Scott": "Short par 4—wedge approach.", "Troy": "High par conversion hole.", "Allen": "Stroke hole—attack pin."}},
            {"num": 13, "par": 4, "hcp": 10, "yds": 335, "tips": {"Scott": "6-point tier—steady fairway placement.", "Troy": "Stroke hole—solid iron into green.", "Allen": "Stroke hole—smooth swing."}},
            {"num": 14, "par": 4, "hcp": 2, "yds": 362, "tips": {"Scott": "HCP #2—9-point tier, guard against right hazard.", "Troy": "Stroke hole—play defensively.", "Allen": "Stroke hole—aim center green."}},
            {"num": 15, "par": 3, "hcp": 16, "yds": 155, "tips": {"Scott": "High par conversion par 3.", "Troy": "Aim center green.", "Allen": "Smooth tempo."}},
            {"num": 16, "par": 5, "hcp": 8, "yds": 429, "tips": {"Scott": "Short par 5—6-point tier, birdie opportunity.", "Troy": "Stroke hole—great point yield hole.", "Allen": "Stroke hole—great net score chance."}},
            {"num": 17, "par": 3, "hcp": 18, "yds": 94, "tips": {"Scott": "Easiest hole on course—attack flag directly!", "Troy": "Short wedge—go for pin.", "Allen": "Easiest HCP rank—great par chance!"}},
            {"num": 18, "par": 4, "hcp": 4, "yds": 353, "tips": {"Scott": "Closing hole—9-point tier, finish strong!", "Troy": "Stroke hole—solid drive to fairway center.", "Allen": "Stroke hole—protect your points lead!"}},
        ],
    },
}

# --- PERSISTENCE HELPERS ---
def load_saved_scores():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                raw_data = json.load(f)
                return {
                    course: {int(h): scores for h, scores in h_dict.items()}
                    for course, h_dict in raw_data.items()
                }
        except Exception:
            pass
    return {c: {} for c in COURSES}

def save_scores_to_disk():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.scores, f)

# --- HELPER CALCULATIONS ---
def get_course_handicap(index, rating, slope, par):
    return int(round(index * (slope / 113) + (rating - par)))

def get_strokes_off_lowest(course_name):
    c = COURSES[course_name]
    ch = {
        p: get_course_handicap(idx, c["rating"], c["slope"], c["par"])
        for p, idx in PLAYERS.items()
    }
    min_ch = min(ch.values())
    return {p: ch[p] - min_ch for p in PLAYERS}

def get_hole_point_value(hcp_rank):
    if hcp_rank <= 6:
        return 9
    elif hcp_rank <= 12:
        return 6
    else:
        return 3

def calculate_hole_points(gross_scores, hcp_rank, stroke_diffs):
    pts_available = get_hole_point_value(hcp_rank)
    net_scores = {}
    for p, g in gross_scores.items():
        stroke = 1 if stroke_diffs[p] >= hcp_rank else 0
        net_scores[p] = g - stroke

    min_net = min(net_scores.values())
    winners = [p for p, net in net_scores.items() if net == min_net]

    pts_won = {p: 0 for p in PLAYERS}
    num_winners = len(winners)

    if num_winners == 1:
        pts_won[winners[0]] = pts_available
    elif num_winners in [2, 3]:
        split_val = pts_available // 3
        for w in winners:
            pts_won[w] = split_val

    return net_scores, pts_won, winners

def get_total_standings():
    totals = {p: 0 for p in PLAYERS}
    for c_name, c_info in COURSES.items():
        s_diffs = get_strokes_off_lowest(c_name)
        for h_num, gross_dict in st.session_state.scores.get(c_name, {}).items():
            if len(gross_dict) == 3:
                h_info = c_info["holes"][h_num - 1]
                _, pts, _ = calculate_hole_points(
                    gross_dict, h_info["hcp"], s_diffs
                )
                for p in PLAYERS:
                    totals[p] += pts[p]
    return totals

def get_course_standings(course_name):
    totals = {p: 0 for p in PLAYERS}
    c_info = COURSES[course_name]
    s_diffs = get_strokes_off_lowest(course_name)
    for h_num, gross_dict in st.session_state.scores.get(course_name, {}).items():
        if len(gross_dict) == 3:
            h_info = c_info["holes"][h_num - 1]
            _, pts, _ = calculate_hole_points(
                gross_dict, h_info["hcp"], s_diffs
            )
            for p in PLAYERS:
                totals[p] += pts[p]
    return totals

def parse_spoken_text(text):
    text_clean = text.lower().strip()
    for word, num in WORD_TO_NUM.items():
        text_clean = re.sub(rf"\b{word}\b", str(num), text_clean)

    scores_found = {}
    player_aliases = {
        "Scott": ["scott", "scw"],
        "Troy": ["troy", "tac"],
        "Allen": ["allen", "atn", "alan"],
    }

    for player_name, aliases in player_aliases.items():
        for alias in aliases:
            match = re.search(rf"{alias}\s*[:=\-]?:\s*(\d+)", text_clean)
            if match:
                val = int(match.group(1))
                if 1 <= val <= 15:
                    scores_found[player_name] = val
                break

    if len(scores_found) == 3:
        return scores_found

    all_numbers = re.findall(r"\b([1-9]|1[0-5])\b", text_clean)
    if len(all_

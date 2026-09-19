import io
import json
import os
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="The Walker Cup", page_icon="⛳", layout="centered"
)

SAVE_FILE = "wc_scores_backup.json"

# --- PLAYER DATA & INITIALS ---
PLAYERS = {"Scott": 17.3, "Troy": 24.2, "Allen": 27.5}
INITIALS = {"Scott": "SCW", "Troy": "TAC", "Allen": "ATN"}

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15
}

# --- COURSE DEFINITIONS WITH OFFICIAL BAYWOOD GREENS SCORECARD & INSIGHTS ---
COURSES = {
    "Frog Hollow (White Tees)": {
        "rating": 70.0,
        "slope": 128,
        "par": 71,
        "holes": [
            {"num": 1, "par": 4, "hcp": 7, "yds": 385, "tips": {"Scott": "Solid opener—favor center-right fairway.", "Troy": "Stroke hole—take advantage of your extra stroke.", "Allen": "You get a stroke—aim middle, avoid right hazard."}},
            {"num": 2, "par": 5, "hcp": 13, "yds": 510, "tips": {"Scott": "Reachable in three—play for center green.", "Troy": "Low handicap scoring hole—be aggressive.", "Allen": "Great scoring hole—keep tee shot in play."}},
            {"num": 3, "par": 3, "hcp": 17, "yds": 155, "tips": {"Scott": "Short iron in hand—favor center green.", "Troy": "Comfortable range—trust your distance.", "Allen": "Smooth swing—target green middle."}},
            {"num": 4, "par": 4, "hcp": 3, "yds": 410, "tips": {"Scott": "Tough handicap hole—bogey is a solid net result.", "Troy": "Stroke hole—play defensively, avoid big numbers.", "Allen": "Key stroke hole—aim for front green edge."}},
            {"num": 5, "par": 4, "hcp": 9, "yds": 375, "tips": {"Scott": "Mid-tier handicap—steady par attempt.", "Troy": "Good opportunity if drive finds fairway.", "Allen": "Stroke hole—focus on approach contact."}},
            {"num": 6, "par": 3, "hcp": 15, "yds": 170, "tips": {"Scott": "Bunker hazard left—miss slightly right.", "Troy": "Solid iron range—aim for green center.", "Allen": "Favor right fringe for safety."}},
            {"num": 7, "par": 4, "hcp": 1, "yds": 430, "tips": {"Scott": "HCP #1—play conservatively for net par.", "Troy": "Stroke hole—take your time off the tee.", "Allen": "Stroke hole—clean fairway contact is priority."}},
            {"num": 8, "par": 5, "hcp": 11, "yds": 525, "tips": {"Scott": "Reachable in 3—play smart layups.", "Troy": "Good historical scoring hole—be aggressive.", "Allen": "Get drive in fairway—solid points chance."}},
            {"num": 9, "par": 4, "hcp": 5, "yds": 395, "tips": {"Scott": "Strong front finish—mind the pin placement.", "Troy": "Stroke hole—keep tee shot in fairway.", "Allen": "Stroke hole—aim left-center fairway."}},
            {"num": 10, "par": 4, "hcp": 8, "yds": 380, "tips": {"Scott": "Good tee shot sets up short approach.", "Troy": "Solid start to back—favor fairway center.", "Allen": "Stroke hole—play for steady bogey/par."}},
            {"num": 11, "par": 3, "hcp": 16, "yds": 160, "tips": {"Scott": "High par conversion hole—trust club selection.", "Troy": "Easy iron into center of green.", "Allen": "Smooth tempo—avoid short bunker."}},
            {"num": 12, "par": 5, "hcp": 12, "yds": 505, "tips": {"Scott": "6-point tier—go for birdie/par path.", "Troy": "Aggressive second shot pays off.", "Allen": "Good hole to make up points."}},
            {"num": 13, "par": 4, "hcp": 2, "yds": 425, "tips": {"Scott": "HCP #2—one of your tougher holes, be careful.", "Troy": "Stroke hole—play defensively.", "Allen": "Stroke hole—avoid hazard on right."}},
            {"num": 14, "par": 4, "hcp": 10, "yds": 370, "tips": {"Scott": "Position over distance off the tee.", "Troy": "Historically score well here—be aggressive.", "Allen": "Stroke hole—smooth fairway wood off tee."}},
            {"num": 15, "par": 3, "hcp": 18, "yds": 145, "tips": {"Scott": "Easiest HCP rank—attack pin directly.", "Troy": "High historical point yield hole.", "Allen": "Great par candidate—stay calm."}},
            {"num": 16, "par": 4, "hcp": 4, "yds": 405, "tips": {"Scott": "Tough approach—guard against short-right.", "Troy": "Stroke hole—take extra club on approach.", "Allen": "Stroke hole—aim for center green."}},
            {"num": 17, "par": 5, "hcp": 14, "yds": 515, "tips": {"Scott": "Long stretch—keep layup in fairway middle.", "Troy": "Scoring opportunity before #18.", "Allen": "Good spot for points—hit fairway."}},
            {"num": 18, "par": 4, "hcp": 6, "yds": 390, "tips": {"Scott": "Closing hole—play for green in regulation.", "Troy": "Stroke hole—finish strong with smart placement.", "Allen": "Stroke hole—protect your points lead."}},
        ],
    },
    "Baywood Greens (White Tees)": {
        "rating": 70.2,
        "slope": 134,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 15, "yds": 349, "tips": {"Scott": "Career avg 4.60—solid opener, favor left-center.", "Troy": "Career avg 4.20—great hole for you; be aggressive.", "Allen": "Career avg 6.00—stroke hole, play for net par."}},
            {"num": 2, "par": 4, "hcp": 9, "yds": 318, "tips": {"Scott": "Career avg 5.20—steady par/bogey history.", "Troy": "Career avg 4.60—stroke hole advantage, attack flag.", "Allen": "Career avg 6.75—stroke hole, play safe layup."}},
            {"num": 3, "par": 4, "hcp": 5, "yds": 395, "tips": {"Scott": "Career avg 5.80—9-point tier, guard against right hazard.", "Troy": "Career avg 5.00—stroke hole, solid par candidate.", "Allen": "Career avg 5.20—stroke hole, smooth tempo."}},
            {"num": 4, "par": 4, "hcp": 3, "yds": 422, "tips": {"Scott": "Career avg 7.20—9-point tier, long approach over traps.", "Troy": "Career avg 5.40—stroke hole, you play this very well.", "Allen": "Career avg 6.50—stroke hole, play center green."}},
            {"num": 5, "par": 5, "hcp": 1, "yds": 515, "tips": {"Scott": "Career avg 8.00—HCP #1 monster, play conservative layups.", "Troy": "Career avg 8.60—stroke hole, avoid water right at all costs.", "Allen": "Career avg 6.60—stroke hole, you score best here!"}},
            {"num": 6, "par": 3, "hcp": 13, "yds": 202, "tips": {"Scott": "Career avg 5.60—long par 3, take extra club.", "Troy": "Career avg 6.20—smooth swing into green center.", "Allen": "Career avg 5.20—great chance for net par."}},
            {"num": 7, "par": 5, "hcp": 7, "yds": 480, "tips": {"Scott": "Career avg 6.25—favor left side of fairway.", "Troy": "Career avg 7.00—stroke hole, use your handicap pad.", "Allen": "Career avg 7.40—stroke hole, play for smart bogey."}},
            {"num": 8, "par": 3, "hcp": 17, "yds": 131, "tips": {"Scott": "Career avg 3.25—YOUR BEST HOLE AT BAYWOOD! Attack flag.", "Troy": "Career avg 3.50—great historical scoring hole for you.", "Allen": "Career avg 4.20—high point yield hole for you."}},
            {"num": 9, "par": 4, "hcp": 11, "yds": 320, "tips": {"Scott": "Career avg 4.75—6-point tier, strong front finish history.", "Troy": "Career avg 4.75—stroke hole, play center green.", "Allen": "Career avg 6.40—stroke hole, take clean contact."}},
            {"num": 10, "par": 4, "hcp": 12, "yds": 360, "tips": {"Scott": "Career avg 5.75—good start to back nine.", "Troy": "Career avg 6.50—stroke hole, favor right fairway.", "Allen": "Career avg 7.00—stroke hole, keep drive in play."}},
            {"num": 11, "par": 3, "hcp": 16, "yds": 139, "tips": {"Scott": "Career avg 3.50—high par rate, attack flag directly.", "Troy": "Career avg 4.75—aim center green, avoid left trap.", "Allen": "Career avg 6.40—focus on smooth iron tempo."}},
            {"num": 12, "par": 4, "hcp": 18, "yds": 288, "tips": {"Scott": "Career avg 5.00—short par 4, wedge in hand.", "Troy": "Career avg 5.00—great scoring opportunity.", "Allen": "Career avg 7.00—easiest HCP rank, attack pin."}},
            {"num": 13, "par": 5, "hcp": 8, "yds": 477, "tips": {"Scott": "Career avg 6.75—tricky green slopes, aim below cup.", "Troy": "Career avg 6.75—stroke hole, favor left side.", "Allen": "Career avg 8.20—stroke hole, play safe bogey."}},
            {"num": 14, "par": 4, "hcp": 2, "yds": 385, "tips": {"Scott": "Career avg 6.50—HCP #2, 9-point tier, play for front green.", "Troy": "Career avg 5.25—stroke hole, high point yield.", "Allen": "Career avg 7.60—stroke hole, play center green."}},
            {"num": 15, "par": 3, "hcp": 14, "yds": 145, "tips": {"Scott": "Career avg 4.25—water left, favor right fringe.", "Troy": "Career avg 4.25—you score very well here; attack.", "Allen": "Career avg 3.50—YOUR BEST PAR 3 AT BAYWOOD!"}},
            {"num": 16, "par": 5, "hcp": 4, "yds": 452, "tips": {"Scott": "Career avg 6.25—9-point tier, reach in 3 clean shots.", "Troy": "Career avg 6.50—stroke hole, good scoring spot.", "Allen": "Career avg 7.25—stroke hole, keep drive in fairway."}},
            {"num": 17, "par": 4, "hcp": 10, "yds": 364, "tips": {"Scott": "Career avg 6.00—penultimate hole, watch right hazard.", "Troy": "Career avg 4.75—stroke hole, aggressive birdie path.", "Allen": "Career avg 6.75—stroke hole, play three clean shots."}},
            {"num": 18, "par": 4, "hcp": 6, "yds": 346, "tips": {"Scott": "Career avg 5.75—9-point tier finish, aim at clubhouse.", "Troy": "Career avg 6.00—stroke hole, finish strong.", "Allen": "Career avg 6.25—stroke hole, solid closing performance."}},
        ],
    },
    "Salt Pond (Black Tees)": {
        "rating": 58.2,
        "slope": 98,
        "par": 61,
        "holes": [
            {"num": 1, "par": 3, "hcp": 13, "yds": 145, "tips": {"Scott": "Career avg 4.50—smooth iron to center green.", "Troy": "Career avg 3.50—great opener for you; aim at flag.", "Allen": "Career avg 7.00—take an extra club off tee."}},
            {"num": 2, "par": 4, "hcp": 3, "yds": 280, "tips": {"Scott": "Career avg 3.50—birdie/par chance; lay up clean.", "Troy": "Career avg 3.00—stroke hole, aggressive birdie path.", "Allen": "Career avg 4.00—stroke hole, great net score hole."}},
            {"num": 3, "par": 3, "hcp": 17, "yds": 125, "tips": {"Scott": "Career avg 4.00—short iron in hand; attack flag.", "Troy": "Career avg 3.00—high par rate; trust distance.", "Allen": "Career avg 4.00—aim for center green."}},
            {"num": 4, "par": 3, "hcp": 9, "yds": 155, "tips": {"Scott": "Career avg 3.00—YOUR BEST PAR 3! Attack pin.", "Troy": "Career avg 3.00—stroke hole, high point yield.", "Allen": "Career avg 4.00—stroke hole, play middle green."}},
            {"num": 5, "par": 4, "hcp": 1, "yds": 295, "tips": {"Scott": "Career avg 4.00—HCP #1; narrow fairway, play smart.", "Troy": "Career avg 4.50—stroke hole, keep drive in play.", "Allen": "Career avg 5.00—stroke hole, play for net par."}},
            {"num": 6, "par": 3, "hcp": 15, "yds": 135, "tips": {"Scott": "Career avg 4.00—favor green center.", "Troy": "Career avg 4.00—solid par history.", "Allen": "Career avg 3.00—GREAT PAR HOLE FOR YOU!"}},
            {"num": 7, "par": 3, "hcp": 7, "yds": 160, "tips": {"Scott": "Career avg 3.50—check wind off trees.", "Troy": "Career avg 4.00—stroke hole, aim center.", "Allen": "Career avg 6.00—stroke hole, club up."}},
            {"num": 8, "par": 4, "hcp": 5, "yds": 275, "tips": {"Scott": "Career avg 4.50—short par 4; layup sets up wedge.", "Troy": "Career avg 3.50—stroke hole, aggressive birdie chance.", "Allen": "Career avg 4.00—stroke hole, great net score history."}},
            {"num": 9, "par": 3, "hcp": 11, "yds": 150, "tips": {"Scott": "Career avg 4.00—solid front finish.", "Troy": "Career avg 5.00—watch front bunker.", "Allen": "Career avg 4.00—smooth swing to middle green."}},
            {"num": 10, "par": 3, "hcp": 14, "yds": 140, "tips": {"Scott": "Career avg 4.00—back 9 opener; clean iron contact.", "Troy": "Career avg 3.50—great start to back nine.", "Allen": "Career avg 4.00—solid par setup."}},
            {"num": 11, "par": 3, "hcp": 17, "yds": 112, "tips": {"Scott": "Career avg 4.00—short hole; attack pin location.", "Troy": "Career avg 4.00—high par conversion rate.", "Allen": "Career avg 3.00—EXCELLENT SCORING HOLE!"}},
            {"num": 12, "par": 3, "hcp": 18, "yds": 115, "tips": {"Scott": "Career avg 3.00—wedge distance; attack flag.", "Troy": "Career avg 2.50—YOUR BEST HOLE AT SALT POND!", "Allen": "Career avg 3.00—great par candidate."}},
            {"num": 13, "par": 3, "hcp": 8, "yds": 165, "tips": {"Scott": "Career avg 3.50—mid-iron test; favor center.", "Troy": "Career avg 3.00—stroke hole, high point yield.", "Allen": "Career avg 3.00—stroke hole, net birdie candidate!"}},
            {"num": 14, "par": 4, "hcp": 2, "yds": 290, "tips": {"Scott": "Career avg 4.50—HCP #2; watch water right.", "Troy": "Career avg 3.50—stroke hole, aggressive drive.", "Allen": "Career avg 5.00—stroke hole, play safe layup."}},
            {"num": 15, "par": 3, "hcp": 16, "yds": 130, "tips": {"Scott": "Career avg 3.00—high par conversion hole.", "Troy": "Career avg 3.00—attack flag directly.", "Allen": "Career avg 3.00—great par performance."}},
            {"num": 16, "par": 3, "hcp": 10, "yds": 150, "tips": {"Scott": "Career avg 5.00—guard against short left.", "Troy": "Career avg 5.00—stroke hole, take extra club.", "Allen": "Career avg 4.00—stroke hole, play green center."}},
            {"num": 17, "par": 4, "hcp": 6, "yds": 270, "tips": {"Scott": "Career avg 5.00—drivable par 4; smart layup.", "Troy": "Career avg 5.50—stroke hole, keep drive straight.", "Allen": "Career avg 4.00—stroke hole, net par candidate."}},
            {"num": 18, "par": 3, "hcp": 12, "yds": 145, "tips": {"Scott": "Career avg 4.50—closing hole; finish strong.", "Troy": "Career avg 6.00—watch right hazard on finish.", "Allen": "Career avg 3.00—YOUR BEST CLOSING HOLE!"}},
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
        for h_num, gross_dict in st.session_state.scores[c_name].items():
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
    for h_num, gross_dict in st.session_state.scores[course_name].items():
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
            match = re.search(rf"{alias}\s*[:=\-]?\s*(\d+)", text_clean)
            if match:
                val = int(match.group(1))
                if 1 <= val <= 15:
                    scores_found[player_name] = val
                break

    if len(scores_found) == 3:
        return scores_found

    all_numbers = re.findall(r"\b([1-9]|1[0-5])\b", text_clean)
    if len(all_numbers) >= 3:
        player_order = ["Scott", "Troy", "Allen"]
        for idx in range(3):
            scores_found[player_order[idx]] = int(all_numbers[idx])

    return scores_found

# --- INITIALIZE SESSION STATE WITH FILE BACKUP ---
if "scores" not in st.session_state:
    st.session_state.scores = load_saved_scores()

if "selected_hole" not in st.session_state:
    st.session_state.selected_hole = 1

if "selected_course" not in st.session_state:
    st.session_state.selected_course = list(COURSES.keys())[0]

selected_course = st.session_state.selected_course
stroke_diffs = get_strokes_off_lowest(selected_course)

course_data = COURSES[selected_course]
hole_num = st.session_state.selected_hole
hole_info = course_data["holes"][hole_num - 1]
pts_val = get_hole_point_value(hole_info["hcp"])

# =========================================================
# 1. TOP HEADER: TITLE & 3 SCORE BOXES
# =========================================================
st.markdown(
    "<h4 style='text-align: center; margin-top: -10px; margin-bottom: 8px;'>⛳ The Walker Cup 2026</h4>",
    unsafe_allow_html=True,
)

live_totals = get_total_standings()
top_score_cols = st.columns(3)
for i, (player, initial) in enumerate(INITIALS.items()):
    with top_score_cols[i]:
        card_html = f"""
        <div style="background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 6px 2px; text-align: center; margin-bottom: 10px;">
            <div style="font-size: 13px; font-weight: 700; color: #94a3b8; letter-spacing: 1px;">{initial}</div>
            <div style="font-size: 28px; font-weight: 900; color: #ffffff; line-height: 1.1;">{live_totals[player]}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# =========================================================
# 2. HOLE INFORMATION & STROKE BADGES
# =========================================================
hdr_html = f"""
<div style="background-color: #15803d; padding: 8px 12px; border-radius: 8px; margin-top: 5px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
    <span style="color: #ffffff; font-size: 20px; font-weight: 800;">⛳ HOLE {hole_num}</span>
    <span style="color: #ffffff; font-size: 14px; font-weight: 700;">PAR <b>{hole_info['par']}</b> &nbsp;|&nbsp; <b>{pts_val} PTS</b> &nbsp;|&nbsp; HCP <b>{hole_info['hcp']}</b></span>
</div>
"""
st.markdown(hdr_html, unsafe_allow_html=True)

troy_strokes = 1 if stroke_diffs["Troy"] >= hole_info["hcp"] else 0
allen_strokes = 1 if stroke_diffs["Allen"] >= hole_info["hcp"] else 0

troy_bg = "#dc2626" if troy_strokes > 0 else "#334155"
allen_bg = "#dc2626" if allen_strokes > 0 else "#334155"

troy_txt = f"+{troy_strokes} Stroke" if troy_strokes > 0 else "Scratch"
allen_txt = f"+{allen_strokes} Stroke" if allen_strokes > 0 else "Scratch"

badge_cols = st.columns(2)
with badge_cols[0]:
    st.markdown(
        f"""
        <div style="background-color: {troy_bg}; color: white; padding: 6px 4px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 8px;">
            <b>Troy</b><br><span style="font-size: 14px; font-weight: 900;">{troy_txt}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with badge_cols[1]:
    st.markdown(
        f"""
        <div style="background-color: {allen_bg}; color: white; padding: 6px 4px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 8px;">
            <b>Allen</b><br><span style="font-size: 14px; font-weight: 900;">{allen_txt}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 2B. 27-YEAR HISTORICAL COURSE INTELLIGENCE TIPS
# =========================================================
hole_tips = hole_info.get("tips", {})
tip_scott = hole_tips.get("Scott", "Play your standard line.")
tip_troy = hole_tips.get("Troy", "Play your standard line.")
tip_allen = hole_tips.get("Allen", "Play your standard line.")

st.markdown(
    f"""
    <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px;">
        <div style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
            📊 27-Year Walker Cup Intelligence:
        </div>
        <div style="font-size: 12px; color: #e2e8f0; margin-bottom: 3px;">
            <b>SCW:</b> {tip_scott}
        </div>
        <div style="font-size: 12px; color: #e2e8f0; margin-bottom: 3px;">
            <b>TAC:</b> {tip_troy}
        </div>
        <div style="font-size: 12px; color: #e2e8f0;">
            <b>ATN:</b> {tip_allen}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. HOLE SELECTION & GROSS SCORE ENTRY
# =========================================================
st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        padding: 4px 0px !important;
        font-size: 13px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.write("**Select Hole:**")

cols_front = st.columns(9)
for h_i in range(1, 10):
    btn_type = (
        "primary" if st.session_state.selected_hole == h_i else "secondary"
    )
    if cols_front[h_i - 1].button(
        str(h_i), key=f"btn_{h_i}", type=btn_type, use_container_width=True
    ):
        st.session_state.selected_hole = h_i
        st.rerun()

cols_back = st.columns(9)
for h_i in range(10, 19):
    btn_type = (
        "primary" if st.session_state.selected_hole == h_i else "secondary"
    )
    if cols_back[h_i - 10].button(
        str(h_i), key=f"btn_{h_i}", type=btn_type, use_container_width=True
    ):
        st.session_state.selected_hole = h_i
        st.rerun()

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.subheader("📝 Enter Gross Scores")

voice_key = f"voice_{selected_course}_{hole_num}"

voice_input = st.text_input(
    "🎙️ Dictate Scores (e.g. 'Scott 4 Troy 6 Allen 5')",
    key=voice_key,
)

saved_scores = st.session_state.scores[selected_course].get(hole_num, {})
current_scores = {p: saved_scores.get(p, hole_info["par"]) for p in PLAYERS}

if voice_input:
    parsed_results = parse_spoken_text(voice_input)
    for p_name, val in parsed_results.items():
        current_scores[p_name] = val
        widget_key = f"{selected_course}_{hole_num}_{p_name}"
        st.session_state[widget_key] = val

cols = st.columns(3)
user_inputs = {}
for i, p in enumerate(PLAYERS.keys()):
    w_key = f"{selected_course}_{hole_num}_{p}"
    if w_key not in st.session_state:
        st.session_state[w_key] = current_scores[p]

    with cols[i]:
        user_inputs[p] = st.number_input(
            f"{p}",
            min_value=1,
            max_value=15,
            key=w_key,
        )

# --- SAVE SCORE & PERSIST TO FILE ---
if st.button("💾 Save Score for Hole", type="primary", use_container_width=True):
    st.session_state.scores[selected_course][hole_num] = user_inputs
    save_scores_to_disk()
    st.success(f"Scores saved for Hole {hole_num}!")

    if st.session_state.selected_hole < 18:
        st.session_state.selected_hole += 1

    st.rerun()

# =========================================================
# 4. CURRENT COURSE LEADERBOARD STANDINGS
# =========================================================
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
st.subheader(f"🏆 Round Standings ({selected_course})")

course_standings = get_course_standings(selected_course)

st.markdown(
    """
    <style>
    .leaderboard-card {
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
    }
    .first-place { background-color: #ffd700; color: #000; }
    .second-place { background-color: #c0c0c0; color: #000; }
    .third-place { background-color: #cd7f32; color: #fff; }
    </style>
""",
    unsafe_allow_html=True,
)

sorted_standings = sorted(
    course_standings.items(), key=lambda x: x[1], reverse=True
)
styles = ["first-place", "second-place", "third-place"]
badges = ["🥇", "🥈", "🥉"]

for rank, (player, score) in enumerate(sorted_standings):
    badge = badges[rank]
    style = styles[rank]
    st.markdown(
        f"""
        <div class="leaderboard-card {style}">
            <span>{badge} #{rank+1} {player}</span>
            <span>{score} PTS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 5. MINI SCORECARD
# =========================================================
st.divider()
st.subheader("📋 Mini Scorecard")

table_rows = ""
for h in course_data["holes"]:
    h_no = h["num"]
    h_val = get_hole_point_value(h["hcp"])

    scott_str, troy_str, allen_str = "-", "-", "-"
    scott_style, troy_style, allen_style = "", "", ""

    if h_no in st.session_state.scores[selected_course]:
        gross = st.session_state.scores[selected_course][h_no]
        if len(gross) == 3:
            nets, pts, winners = calculate_hole_points(
                gross, h["hcp"], stroke_diffs
            )

            scott_str = f"{nets['Scott']} ({gross['Scott']})"
            troy_str = f"{nets['Troy']} ({gross['Troy']})"
            allen_str = f"{nets['Allen']} ({gross['Allen']})"

            is_tie = len(winners) > 1

            if "Scott" in winners:
                scott_style = (
                    "background-color: #eab308; color: #000000; font-weight: bold;"
                    if is_tie
                    else "background-color: #15803d; color: #ffffff; font-weight: bold;"
                )
            if "Troy" in winners:
                troy_style = (
                    "background-color: #eab308; color: #000000; font-weight: bold;"
                    if is_tie
                    else "background-color: #15803d; color: #ffffff; font-weight: bold;"
                )
            if "Allen" in winners:
                allen_style = (
                    "background-color: #eab308; color: #000000; font-weight: bold;"
                    if is_tie
                    else "background-color: #15803d; color: #ffffff; font-weight: bold;"
                )

    row_html = f"""
        <tr>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;"><b>#{h_no}</b></td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['yds']}</td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['par']}</td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['hcp']}</td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;"><b>{h_val}</b></td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {scott_style}">{scott_str}</td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {troy_style}">{troy_str}</td>
            <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {allen_style}">{allen_str}</td>
        </tr>
    """
    table_rows += row_html

full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: sans-serif; background-color: transparent; color: #ffffff; margin: 0; padding: 0; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background-color: #0f172a; color: #ffffff; padding: 8px 4px; border: 1px solid #334155; font-size: 12px; }}
    </style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>Hole</th>
                <th>Yds</th>
                <th>Par</th>
                <th>Hcp</th>
                <th>Pts</th>
                <th>Scott</th>
                <th>Troy</th>
                <th>Allen</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</body>
</html>
"""

components.html(full_html, height=520, scrolling=True)

# =========================================================
# 6. COURSE SELECTOR & RESET BUTTON (BOTTOM)
# =========================================================
st.divider()

b_col1, b_col2 = st.columns(2)
with b_col1:
    selected_course_input = st.selectbox(
        "⚙️ Select Course / Round",
        list(COURSES.keys()),
        index=list(COURSES.keys()).index(st.session_state.selected_course),
        key="course_picker_bottom",
    )
    if selected_course_input != st.session_state.selected_course:
        st.session_state.selected_course = selected_course_input
        st.rerun()

with b_col2:
    st.write("&nbsp;")
    if st.button("🔄 Reset Tournament Scores", use_container_width=True):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        st.session_state.scores = {c: {} for c in COURSES}
        st.rerun()

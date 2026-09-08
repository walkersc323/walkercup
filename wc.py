import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="The Walker Cup", page_icon="⛳", layout="centered"
)

# --- PLAYER DATA & INITIALS ---
PLAYERS = {"Scott": 17.3, "Troy": 24.2, "Allen": 27.5}
INITIALS = {"Scott": "SCW", "Troy": "TAC", "Allen": "ATN"}

# Word-to-Number mapping for dictation
WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15
}

# --- COURSE DEFINITIONS ---
COURSES = {
    "Frog Hollow (White Tees)": {
        "rating": 70.0,
        "slope": 128,
        "par": 71,
        "holes": [
            {"num": 1, "par": 4, "hcp": 7, "yds": 385},
            {"num": 2, "par": 5, "hcp": 13, "yds": 510},
            {"num": 3, "par": 3, "hcp": 17, "yds": 155},
            {"num": 4, "par": 4, "hcp": 3, "yds": 410},
            {"num": 5, "par": 4, "hcp": 9, "yds": 375},
            {"num": 6, "par": 3, "hcp": 15, "yds": 170},
            {"num": 7, "par": 4, "hcp": 1, "yds": 430},
            {"num": 8, "par": 5, "hcp": 11, "yds": 525},
            {"num": 9, "par": 4, "hcp": 5, "yds": 395},
            {"num": 10, "par": 4, "hcp": 8, "yds": 380},
            {"num": 11, "par": 3, "hcp": 16, "yds": 160},
            {"num": 12, "par": 5, "hcp": 12, "yds": 505},
            {"num": 13, "par": 4, "hcp": 2, "yds": 425},
            {"num": 14, "par": 4, "hcp": 10, "yds": 370},
            {"num": 15, "par": 3, "hcp": 18, "yds": 145},
            {"num": 16, "par": 4, "hcp": 4, "yds": 405},
            {"num": 17, "par": 5, "hcp": 14, "yds": 515},
            {"num": 18, "par": 4, "hcp": 6, "yds": 390},
        ],
    },
    "Baywood Greens (White Tees)": {
        "rating": 70.2,
        "slope": 134,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 9, "yds": 375},
            {"num": 2, "par": 4, "hcp": 5, "yds": 390},
            {"num": 3, "par": 3, "hcp": 15, "yds": 165},
            {"num": 4, "par": 5, "hcp": 1, "yds": 535},
            {"num": 5, "par": 4, "hcp": 11, "yds": 360},
            {"num": 6, "par": 3, "hcp": 17, "yds": 150},
            {"num": 7, "par": 4, "hcp": 7, "yds": 380},
            {"num": 8, "par": 5, "hcp": 13, "yds": 505},
            {"num": 9, "par": 4, "hcp": 3, "yds": 410},
            {"num": 10, "par": 4, "hcp": 10, "yds": 370},
            {"num": 11, "par": 3, "hcp": 18, "yds": 140},
            {"num": 12, "par": 5, "hcp": 2, "yds": 540},
            {"num": 13, "par": 4, "hcp": 8, "yds": 385},
            {"num": 14, "par": 3, "hcp": 16, "yds": 155},
            {"num": 15, "par": 4, "hcp": 4, "yds": 400},
            {"num": 16, "par": 4, "hcp": 12, "yds": 365},
            {"num": 17, "par": 5, "hcp": 6, "yds": 520},
            {"num": 18, "par": 4, "hcp": 14, "yds": 355},
        ],
    },
    "Salt Pond (Black Tees)": {
        "rating": 58.2,
        "slope": 98,
        "par": 61,
        "holes": [
            {"num": 1, "par": 3, "hcp": 13, "yds": 145},
            {"num": 2, "par": 4, "hcp": 3, "yds": 280},
            {"num": 3, "par": 3, "hcp": 17, "yds": 125},
            {"num": 4, "par": 3, "hcp": 9, "yds": 155},
            {"num": 5, "par": 4, "hcp": 1, "yds": 295},
            {"num": 6, "par": 3, "hcp": 15, "yds": 135},
            {"num": 7, "par": 3, "hcp": 7, "yds": 160},
            {"num": 8, "par": 4, "hcp": 5, "yds": 275},
            {"num": 9, "par": 3, "hcp": 11, "yds": 150},
            {"num": 10, "par": 3, "hcp": 14, "yds": 140},
            {"num": 11, "par": 4, "hcp": 4, "yds": 285},
            {"num": 12, "par": 3, "hcp": 18, "yds": 115},
            {"num": 13, "par": 3, "hcp": 8, "yds": 165},
            {"num": 14, "par": 4, "hcp": 2, "yds": 290},
            {"num": 15, "par": 3, "hcp": 16, "yds": 130},
            {"num": 16, "par": 3, "hcp": 10, "yds": 150},
            {"num": 17, "par": 4, "hcp": 6, "yds": 270},
            {"num": 18, "par": 3, "hcp": 12, "yds": 145},
        ],
    },
}


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


# --- INITIALIZE SESSION STATE ---
if "scores" not in st.session_state:
    st.session_state.scores = {c: {} for c in COURSES}

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
# 2. HOLE INFORMATION (DARK GREEN BANNER WITH HCP) & STROKE BADGES
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
        <div style="background-color: {troy_bg}; color: white; padding: 6px 4px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 12px;">
            <b>Troy</b><br><span style="font-size: 14px; font-weight: 900;">{troy_txt}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with badge_cols[1]:
    st.markdown(
        f"""
        <div style="background-color: {allen_bg}; color: white; padding: 6px 4px; border-radius: 6px; text-align: center; font-size: 13px; margin-bottom: 12px;">
            <b>Allen</b><br><span style="font-size: 14px; font-weight: 900;">{allen_txt}</span>
        </div>
        """,
        unsafe_allow_html=True,
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

# --- AUTO-ADVANCE HOLE ON SAVE ---
if st.button("💾 Save Score for Hole", type="primary", use_container_width=True):
    st.session_state.scores[selected_course][hole_num] = user_inputs
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
# 6. COURSE SELECTOR (BOTTOM)
# =========================================================
st.divider()
selected_course_input = st.selectbox(
    "⚙️ Select Course / Round",
    list(COURSES.keys()),
    index=list(COURSES.keys()).index(st.session_state.selected_course),
    key="course_picker_bottom",
)

if selected_course_input != st.session_state.selected_course:
    st.session_state.selected_course = selected_course_input
    st.rerun()

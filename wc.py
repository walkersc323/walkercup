import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="The Walker Cup", page_icon="⛳", layout="centered"
)

# --- PLAYER DATA & HANDICAPS ---
PLAYERS = {"Scott": 17.3, "Troy": 24.2, "Allen": 27.5}

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
    split_pts = int(round(pts_available / len(winners)))
    for w in winners:
        pts_won[w] = split_pts

    return net_scores, pts_won


# --- INITIALIZE SESSION STATE ---
if "scores" not in st.session_state:
    st.session_state.scores = {c: {} for c in COURSES}

# --- HEADER & COURSE SELECTION ---
st.title("⛳ The Walker Cup")
selected_course = st.selectbox("Select Course / Round", list(COURSES.keys()))
stroke_diffs = get_strokes_off_lowest(selected_course)

tab1, tab2 = st.tabs(["📝 Hole Scoring", "🏆 Leaderboard"])

# =========================================================
# TAB 1: HOLE SCORING & MINI SCORECARD
# =========================================================
with tab1:
    course_data = COURSES[selected_course]

    col_selector, _ = st.columns([2, 1])
    with col_selector:
        hole_num = st.number_input(
            "Select Hole Number", min_value=1, max_value=18, value=1, step=1
        )

    hole_info = course_data["holes"][hole_num - 1]
    pts_val = get_hole_point_value(hole_info["hcp"])

    st.markdown(
        f"""
        <div style="background-color: #1e293b; padding: 16px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
            <h1 style="color: #ffffff; margin: 0; font-size: 38px; font-weight: 800;">⛳ HOLE {hole_num}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(label="PAR", value=hole_info["par"])
        st.metric(label="HANDICAP RANK", value=f"#{hole_info['hcp']}")
    with m_col2:
        st.metric(label="YARDAGE", value=f"{hole_info['yds']} yds")
        st.metric(label="HOLE VALUE", value=f"{pts_val} PTS")

    st.divider()
    st.write("**Strokes Received This Hole:**")

    stroke_cols = st.columns(3)
    for i, p in enumerate(PLAYERS.keys()):
        strokes_on_hole = 1 if stroke_diffs[p] >= hole_info["hcp"] else 0
        badge_color = "#10b981" if strokes_on_hole > 0 else "#64748b"
        badge_text = (
            f"+{strokes_on_hole} Stroke" if strokes_on_hole > 0 else "Scratch"
        )

        with stroke_cols[i]:
            st.markdown(
                f"""
                <div style="background-color: {badge_color}; color: white; padding: 8px 4px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 14px;">
                    {p}<br><span style="font-size: 16px; font-weight: 900;">{badge_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("📝 Enter Gross Scores")

    voice_input = st.text_input(
        "🎙️ Spoken Score Entry (e.g., 'Scott 4, Troy 5, Allen 5')", key="voice"
    )

    default_scores = {p: hole_info["par"] for p in PLAYERS}
    if voice_input:
        for p in PLAYERS:
            match = re.search(rf"{p}\s*(\d+)", voice_input, re.IGNORECASE)
            if match:
                default_scores[p] = int(match.group(1))

    cols = st.columns(3)
    user_inputs = {}
    for i, p in enumerate(PLAYERS.keys()):
        with cols[i]:
            user_inputs[p] = st.number_input(
                f"{p}",
                min_value=1,
                max_value=15,
                value=default_scores[p],
                key=f"{selected_course}_{hole_num}_{p}",
            )

    if st.button("💾 Save Score for Hole", type="primary", use_container_width=True):
        st.session_state.scores[selected_course][hole_num] = user_inputs
        st.success(f"Scores saved for Hole {hole_num}!")

    # --- MINI SCORECARD TABLE ---
    st.divider()
    st.subheader("📋 Mini Scorecard")

    table_rows = ""
    for h in course_data["holes"]:
        h_no = h["num"]
        h_val = get_hole_point_value(h["hcp"])

        scott_str, troy_str, allen_str = "-", "-", "-"
        scott_win, troy_win, allen_win = False, False, False

        if h_no in st.session_state.scores[selected_course]:
            gross = st.session_state.scores[selected_course][h_no]
            nets, pts = calculate_hole_points(gross, h["hcp"], stroke_diffs)

            scott_str = f"{nets['Scott']} ({gross['Scott']})"
            troy_str = f"{nets['Troy']} ({gross['Troy']})"
            allen_str = f"{nets['Allen']} ({gross['Allen']})"

            if pts["Scott"] > 0:
                scott_win = True
            if pts["Troy"] > 0:
                troy_win = True
            if pts["Allen"] > 0:
                allen_win = True

        row_html = f"""
            <tr>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;"><b>#{h_no}</b></td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['yds']}</td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['par']}</td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;">{h['hcp']}</td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center;"><b>{h_val}</b></td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {'background-color: #15803d; color: white; font-weight: bold;' if scott_win else ''}">{scott_str}</td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {'background-color: #15803d; color: white; font-weight: bold;' if troy_win else ''}">{troy_str}</td>
                <td style="padding: 6px 4px; border: 1px solid #334155; text-align: center; {'background-color: #15803d; color: white; font-weight: bold;' if allen_win else ''}">{allen_str}</td>
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
# TAB 2: LEADERBOARD
# =========================================================
with tab2:
    st.subheader("🏆 Tournament Standings")

    total_standings = {p: 0 for p in PLAYERS}

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

    for c_name, c_info in COURSES.items():
        s_diffs = get_strokes_off_lowest(c_name)
        for h_num, gross_dict in st.session_state.scores[c_name].items():
            h_info = c_info["holes"][h_num - 1]
            _, pts = calculate_hole_points(gross_dict, h_info["hcp"], s_diffs)
            for p in PLAYERS:
                total_standings[p] += int(round(pts[p]))

    sorted_standings = sorted(
        total_standings.items(), key=lambda x: x[1], reverse=True
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

    st.divider()
    st.subheader("📊 Round-by-Round Breakdown")

    for c_name, c_info in COURSES.items():
        st.markdown(f"**{c_name}**")
        s_diffs = get_strokes_off_lowest(c_name)
        c_pts = {p: 0 for p in PLAYERS}

        for h_num, gross_dict in st.session_state.scores[c_name].items():
            h_info = c_info["holes"][h_num - 1]
            _, pts = calculate_hole_points(gross_dict, h_info["hcp"], s_diffs)
            for p in PLAYERS:
                c_pts[p] += int(round(pts[p]))

        m_cols = st.columns(3)
        for i, p in enumerate(PLAYERS.keys()):
            with m_cols[i]:
                st.metric(label=p, value=f"{c_pts[p]} pts")
        st.write("---")

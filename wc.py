import re
import streamlit as st

st.set_page_config(
    page_title="Walker Cup Tournament", page_icon="⛳", layout="centered"
)

# ---------------------------------------------------------
# 1. PLAYERS & COURSE DATA SETTINGS
# ---------------------------------------------------------
PLAYERS = {"Scott": 17.3, "Troy": 24.2, "Allen": 27.5}

COURSES = {
    "Round 1: Frog Hollow": {
        "rating": 70.0,
        "slope": 128,
        "par": 71,
        "holes": [
            {"num": 1, "par": 4, "hcp": 8, "yds": 352},
            {"num": 2, "par": 5, "hcp": 6, "yds": 480},
            {"num": 3, "par": 3, "hcp": 16, "yds": 145},
            {"num": 4, "par": 4, "hcp": 2, "yds": 405},
            {"num": 5, "par": 5, "hcp": 10, "yds": 470},
            {"num": 6, "par": 3, "hcp": 12, "yds": 180},
            {"num": 7, "par": 4, "hcp": 4, "yds": 357},
            {"num": 8, "par": 3, "hcp": 18, "yds": 135},
            {"num": 9, "par": 4, "hcp": 14, "yds": 350},
            {"num": 10, "par": 4, "hcp": 7, "yds": 370},
            {"num": 11, "par": 5, "hcp": 13, "yds": 514},
            {"num": 12, "par": 4, "hcp": 11, "yds": 360},
            {"num": 13, "par": 4, "hcp": 9, "yds": 330},
            {"num": 14, "par": 3, "hcp": 15, "yds": 155},
            {"num": 15, "par": 4, "hcp": 3, "yds": 417},
            {"num": 16, "par": 3, "hcp": 17, "yds": 186},
            {"num": 17, "par": 4, "hcp": 1, "yds": 409},
            {"num": 18, "par": 5, "hcp": 5, "yds": 530},
        ],
    },
    "Round 2: Baywood Greens": {
        "rating": 70.2,
        "slope": 134,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 13, "yds": 349},
            {"num": 2, "par": 4, "hcp": 11, "yds": 318},
            {"num": 3, "par": 4, "hcp": 3, "yds": 395},
            {"num": 4, "par": 4, "hcp": 1, "yds": 422},
            {"num": 5, "par": 5, "hcp": 5, "yds": 515},
            {"num": 6, "par": 3, "hcp": 15, "yds": 202},
            {"num": 7, "par": 5, "hcp": 7, "yds": 480},
            {"num": 8, "par": 3, "hcp": 17, "yds": 131},
            {"num": 9, "par": 4, "hcp": 9, "yds": 320},
            {"num": 10, "par": 4, "hcp": 4, "yds": 360},
            {"num": 11, "par": 3, "hcp": 16, "yds": 139},
            {"num": 12, "par": 4, "hcp": 18, "yds": 288},
            {"num": 13, "par": 5, "hcp": 14, "yds": 477},
            {"num": 14, "par": 4, "hcp": 2, "yds": 385},
            {"num": 15, "par": 3, "hcp": 12, "yds": 145},
            {"num": 16, "par": 5, "hcp": 10, "yds": 452},
            {"num": 17, "par": 4, "hcp": 8, "yds": 364},
            {"num": 18, "par": 4, "hcp": 6, "yds": 346},
        ],
    },
    "Round 3: Salt Pond": {
        "rating": 58.2,
        "slope": 98,
        "par": 61,
        "holes": [
            {"num": 1, "par": 3, "hcp": 6, "yds": 151},
            {"num": 2, "par": 3, "hcp": 18, "yds": 113},
            {"num": 3, "par": 3, "hcp": 8, "yds": 180},
            {"num": 4, "par": 3, "hcp": 16, "yds": 104},
            {"num": 5, "par": 4, "hcp": 2, "yds": 260},
            {"num": 6, "par": 3, "hcp": 14, "yds": 150},
            {"num": 7, "par": 4, "hcp": 10, "yds": 200},
            {"num": 8, "par": 3, "hcp": 4, "yds": 184},
            {"num": 9, "par": 3, "hcp": 12, "yds": 125},
            {"num": 10, "par": 3, "hcp": 7, "yds": 177},
            {"num": 11, "par": 3, "hcp": 17, "yds": 112},
            {"num": 12, "par": 4, "hcp": 5, "yds": 198},
            {"num": 13, "par": 4, "hcp": 11, "yds": 212},
            {"num": 14, "par": 4, "hcp": 13, "yds": 198},
            {"num": 15, "par": 3, "hcp": 15, "yds": 140},
            {"num": 16, "par": 4, "hcp": 1, "yds": 241},
            {"num": 17, "par": 3, "hcp": 9, "yds": 177},
            {"num": 18, "par": 4, "hcp": 3, "yds": 252},
        ],
    },
}

# Initialize session state for scorekeeping
if "scores" not in st.session_state:
    st.session_state.scores = {c: {} for c in COURSES.keys()}

# ---------------------------------------------------------
# 2. CALCULATION HELPER FUNCTIONS
# ---------------------------------------------------------


def get_strokes_off_lowest(course_name):
    c_info = COURSES[course_name]
    course_hcps = {}
    for p, idx in PLAYERS.items():
        ch = round(idx * (c_info["slope"] / 113) + (c_info["rating"] - c_info["par"]))
        course_hcps[p] = ch

    lowest = min(course_hcps.values())
    return {p: ch - lowest for p, ch in course_hcps.items()}


def get_hole_point_value(hcp_rank):
    if hcp_rank <= 6:
        return 9
    elif hcp_rank <= 12:
        return 6
    else:
        return 3


def calculate_hole_points(gross_scores, hole_hcp, stroke_diffs):
    net_scores = {}
    for p, gross in gross_scores.items():
        strokes_received = 1 if stroke_diffs[p] >= hole_hcp else 0
        net_scores[p] = gross - strokes_received

    min_net = min(net_scores.values())
    winners = [p for p, net in net_scores.items() if net == min_net]

    max_pts = get_hole_point_value(hole_hcp)
    pts_earned = {p: 0.0 for p in PLAYERS.keys()}

    if len(winners) == 1:
        pts_earned[winners[0]] = float(max_pts)
    else:
        split_val = max_pts / 3.0
        for w in winners:
            pts_earned[w] = split_val

    return net_scores, pts_earned


# ---------------------------------------------------------
# 3. APP FRONTEND INTERFACE
# ---------------------------------------------------------
st.title("⛳ The Walker Cup")

selected_course = st.selectbox("Select Round", list(COURSES.keys()))
stroke_diffs = get_strokes_off_lowest(selected_course)

tab1, tab2 = st.tabs([" Hole Scoring", " Leaderboard"])

with tab1:
    course_data = COURSES[selected_course]

    # Large Mobile Hole Selector
    col_selector, _ = st.columns([2, 1])
    with col_selector:
        hole_num = st.number_input(
            "Select Hole Number", min_value=1, max_value=18, value=1, step=1
        )

    hole_info = course_data["holes"][hole_num - 1]
    pts_val = get_hole_point_value(hole_info["hcp"])

    # High-Visibility Mobile Header Card
    st.markdown(
        f"""
        <div style="
            background-color: #1e293b; 
            padding: 16px; 
            border-radius: 12px; 
            text-align: center; 
            margin-bottom: 15px; 
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
            <h1 style="color: #ffffff; margin: 0; font-size: 38px; font-weight: 800;">⛳ HOLE {hole_num}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Large Stat Cards (2x2 Grid for Mobile Screens)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(label="PAR", value=hole_info["par"])
        st.metric(label="HANDICAP RANK", value=f"#{hole_info['hcp']}")
    with m_col2:
        st.metric(label="YARDAGE", value=f"{hole_info['yds']} yds")
        st.metric(label="HOLE VALUE", value=f"{pts_val} PTS")

    # Handicap Stroke Badges for this Hole
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
                <div style="
                    background-color: {badge_color}; 
                    color: white; 
                    padding: 8px 4px; 
                    border-radius: 8px; 
                    text-align: center; 
                    font-weight: bold;
                    font-size: 14px;
                ">
                    {p}<br><span style="font-size: 16px; font-weight: 900;">{badge_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("📝 Enter Gross Scores")

    # Voice Input Handler
    voice_input = st.text_input(
        "🎙️ Spoken Score Entry (e.g., 'Scott 4, Troy 5, Allen 5')", key="voice"
    )

    default_scores = {p: hole_info["par"] for p in PLAYERS}
    if voice_input:
        for p in PLAYERS:
            match = re.search(rf"{p}\s*(\d+)", voice_input, re.IGNORECASE)
            if match:
                default_scores[p] = int(match.group(1))

    # Large Dropdown/Number Score Inputs
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

# ---------------------------------------------------------
    # MINI SCORECARD TABLE ON LANDING PAGE
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📋 Mini Scorecard")

    table_rows = ""
    for h in course_data["holes"]:
        h_no = h["num"]
        h_val = get_hole_point_value(h["hcp"])

        scott_str = "-"
        troy_str = "-"
        allen_str = "-"
        scott_win = False
        troy_win = False
        allen_win = False

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

    import streamlit.components.v1 as components

    components.html(full_html, height=520, scrolling=True)

    for h in course_data["holes"]:
        h_no = h["num"]
        h_val = get_hole_point_value(h["hcp"])

        scott_str = "-"
        troy_str = "-"
        allen_str = "-"
        scott_win = False
        troy_win = False
        allen_win = False

        if h_no in st.session_state.scores[selected_course]:
            gross = st.session_state.scores[selected_course][h_no]
            nets, pts = calculate_hole_points(gross, h["hcp"], stroke_diffs)

            scott_str = f"{nets['Scott']} ({gross['Scott']})"
            troy_str = f"{nets['Troy']} ({gross['Troy']})"
            allen_str = f"{nets['Allen']} ({gross['Allen']})"

            # Check winner highlighting
            if pts["Scott"] > 0:
                scott_win = True
            if pts["Troy"] > 0:
                troy_win = True
            if pts["Allen"] > 0:
                allen_win = True

        row_html = f"""
            <tr>
                <td><b>#{h_no}</b></td>
                <td>{h['yds']}</td>
                <td>{h['par']}</td>
                <td>{h['hcp']}</td>
                <td><b>{h_val}</b></td>
                <td class="{'winner-cell' if scott_win else ''}">{scott_str}</td>
                <td class="{'winner-cell' if troy_win else ''}">{troy_str}</td>
                <td class="{'winner-cell' if allen_win else ''}">{allen_str}</td>
            </tr>
        """
        table_html += row_html

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

with tab2:
    st.subheader("🏆 Tournament Standings")

    total_standings = {p: 0 for p in PLAYERS}

    # Custom styling for leaderboard cards
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

    # Calculate overall scores
    for c_name, c_info in COURSES.items():
        s_diffs = get_strokes_off_lowest(c_name)
        for h_num, gross_dict in st.session_state.scores[c_name].items():
            h_info = c_info["holes"][h_num - 1]
            _, pts = calculate_hole_points(gross_dict, h_info["hcp"], s_diffs)
            for p in PLAYERS:
                total_standings[p] += int(round(pts[p]))

    # Rank players
    sorted_standings = sorted(
        total_standings.items(), key=lambda x: x[1], reverse=True
    )
    styles = ["first-place", "second-place", "third-place"]
    badges = ["🥇", "🥈", "🥉"]

    # Display Top Standings Cards
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

    # Detailed Table Breakdown per Round
    for c_name, c_info in COURSES.items():
        st.markdown(f"**{c_name}**")
        s_diffs = get_strokes_off_lowest(c_name)
        c_pts = {p: 0 for p in PLAYERS}

        for h_num, gross_dict in st.session_state.scores[c_name].items():
            h_info = c_info["holes"][h_num - 1]
            _, pts = calculate_hole_points(gross_dict, h_info["hcp"], s_diffs)
            for p in PLAYERS:
                c_pts[p] += int(round(pts[p]))

        # Display as a compact metric row
        m_cols = st.columns(3)
        for i, p in enumerate(PLAYERS.keys()):
            with m_cols[i]:
                st.metric(label=p, value=f"{c_pts[p]} pts")
        st.write("---")

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

# --- COURSE DEFINITIONS WITH HISTORICAL 27-YEAR HOLE INSIGHTS ---
COURSES = {
    "Frog Hollow (White Tees)": {
        "rating": 70.0,
        "slope": 128,
        "par": 71,
        "holes": [
            {"num": 1, "par": 4, "hcp": 7, "yds": 385, "tips": {"Scott": "Solid starting hole—play for center green.", "Troy": "Stroke hole—take advantage of the extra pad.", "Allen": "You get a stroke here—aim middle, avoid right."}},
            {"num": 2, "par": 5, "hcp": 13, "yds": 510, "tips": {"Scott": "Good birdie/par opportunity—stay in play off tee.", "Troy": "Historical low-scoring hole—be aggressive.", "Allen": "Great scoring hole for you—keep it straight."}},
            {"num": 3, "par": 3, "hcp": 17, "yds": 155, "tips": {"Scott": "Short iron in—favor the center.", "Troy": "Historically tricky distance—trust your club.", "Allen": "Smooth swing—no need to overpower."}},
            {"num": 4, "par": 4, "hcp": 3, "yds": 410, "tips": {"Scott": "Tough handicap hole—bogey is a decent result.", "Troy": "Stroke hole—play smart, avoid big numbers.", "Allen": "Key stroke hole—target front edge."}},
            {"num": 5, "par": 4, "hcp": 9, "yds": 375, "tips": {"Scott": "Mid-tier handicap—steady par attempt.", "Troy": "Good opportunity if you hit the fairway.", "Allen": "You get a stroke here—focus on approach."}},
            {"num": 6, "par": 3, "hcp": 15, "yds": 170, "tips": {"Scott": "Bunker hazard left—miss slightly right.", "Troy": "Comfortable range—aim for green center.", "Allen": "Favor right side for safety."}},
            {"num": 7, "par": 4, "hcp": 1, "yds": 430, "tips": {"Scott": "HCP #1—play conservatively for net par.", "Troy": "Stroke hole—take your time off the tee.", "Allen": "Stroke hole—focus on clean contact."}},
            {"num": 8, "par": 5, "hcp": 11, "yds": 525, "tips": {"Scott": "Reachable in three—play smart layups.", "Troy": "Good scoring hole historically—be aggressive.", "Allen": "Get it in fairway—solid points chance."}},
            {"num": 9, "par": 4, "hcp": 5, "yds": 395, "tips": {"Scott": "Strong finish to front—mind the pin location.", "Troy": "Stroke hole—keep tee shot in play.", "Allen": "Stroke hole—aim left-center fairway."}},
            {"num": 10, "par": 4, "hcp": 8, "yds": 380, "tips": {"Scott": "Nice tee shot sets up short iron approach.", "Troy": "Solid start to back—favor fairway center.", "Allen": "You get a stroke—play for steady bogey/par."}},
            {"num": 11, "par": 3, "hcp": 16, "yds": 160, "tips": {"Scott": "High par conversion hole—trust your distance.", "Troy": "Easy iron into center green.", "Allen": "Focus on smooth tempo."}},
            {"num": 12, "par": 5, "hcp": 12, "yds": 505, "tips": {"Scott": "9-point scoring tier—go for birdie path.", "Troy": "Aggressive second shot can pay off.", "Allen": "Good hole to make up ground."}},
            {"num": 13, "par": 4, "hcp": 2, "yds": 425, "tips": {"Scott": "HCP #2—one of your tougher holes, be careful.", "Troy": "Stroke hole—play defensively.", "Allen": "Stroke hole—avoid hazard right."}},
            {"num": 14, "par": 4, "hcp": 10, "yds": 370, "tips": {"Scott": "Position over distance off tee.", "Troy": "You score well here—be aggressive.", "Allen": "Stroke hole—smooth fairway wood off tee."}},
            {"num": 15, "par": 3, "hcp": 18, "yds": 145, "tips": {"Scott": "Easiest HCP rank—aim straight at flag.", "Troy": "Historically high point yield hole.", "Allen": "Great par chance—stay calm."}},
            {"num": 16, "par": 4, "hcp": 4, "yds": 405, "tips": {"Scott": "Tough approach—guard against short right.", "Troy": "Stroke hole—take extra club on approach.", "Allen": "Stroke hole—aim for center green."}},
            {"num": 17, "par": 5, "hcp": 14, "yds": 515, "tips": {"Scott": "Long stretch—keep layup in middle.", "Troy": "Scoring opportunity before 18.", "Allen": "Good spot for points—hit fairway."}},
            {"num": 18, "par": 4, "hcp": 6, "yds": 390, "tips": {"Scott": "Closing hole—play for solid green in regulation.", "Troy": "Stroke hole—finish strong with smart placement.", "Allen": "Stroke hole—protect your points lead."}},
        ],
    },
    "Baywood Greens (White Tees)": {
        "rating": 70.2,
        "slope": 134,
        "par": 72,
        "holes": [
            {"num": 1, "par": 4, "hcp": 9, "yds": 375, "tips": {"Scott": "Gentle opener—favor right-center fairway.", "Troy": "Good starting hole—smooth swing.", "Allen": "You get a stroke—aim middle."}},
            {"num": 2, "par": 4, "hcp": 5, "yds": 390, "tips": {"Scott": "Tough approach over fairway traps.", "Troy": "Stroke hole—take your extra shot advantage.", "Allen": "Stroke hole—play safe layup if needed."}},
            {"num": 3, "par": 3, "hcp": 15, "yds": 165, "tips": {"Scott": "High green hit percentage—aim dead center.", "Troy": "Good par candidate—trust distance.", "Allen": "Smooth swing into center."}},
            {"num": 4, "par": 5, "hcp": 1, "yds": 535, "tips": {"Scott": "HCP #1—tough water threat, play conservative.", "Troy": "Stroke hole—avoid water right at all costs.", "Allen": "Stroke hole—three safe shots to green."}},
            {"num": 5, "par": 4, "hcp": 11, "yds": 360, "tips": {"Scott": "One of your tougher holes—be careful.", "Troy": "You score well; be aggressive.", "Allen": "Stroke hole—good approach angle from left."}},
            {"num": 6, "par": 3, "hcp": 17, "yds": 150, "tips": {"Scott": "Short par 3—target pin.", "Troy": "High point return historically.", "Allen": "Easy par chance."}},
            {"num": 7, "par": 4, "hcp": 7, "yds": 380, "tips": {"Scott": "Mid-handicap challenge—favor left fairway.", "Troy": "Stroke hole—keep drive straight.", "Allen": "Stroke hole—play smart bogey."}},
            {"num": 8, "par": 5, "hcp": 13, "yds": 505, "tips": {"Scott": "Big scoring hole—reach in 3 easily.", "Troy": "Historically yields birdies/pars.", "Allen": "Great point opportunity."}},
            {"num": 9, "par": 4, "hcp": 3, "yds": 410, "tips": {"Scott": "Long par 4—play for front green.", "Troy": "Stroke hole—don't force approach.", "Allen": "Stroke hole—take extra club."}},
            {"num": 10, "par": 4, "hcp": 10, "yds": 370, "tips": {"Scott": "Solid back nine opener.", "Troy": "You score well here—stay aggressive.", "Allen": "Stroke hole—keep drive in play."}},
            {"num": 11, "par": 3, "hcp": 18, "yds": 140, "tips": {"Scott": "Easiest hole on course—attack flag.", "Troy": "High par conversion rate.", "Allen": "Good chance for net birdie."}},
            {"num": 12, "par": 5, "hcp": 2, "yds": 540, "tips": {"Scott": "HCP #2 monster—play three controlled shots.", "Troy": "Stroke hole—lay up safely.", "Allen": "Stroke hole—avoid fairway bunkers."}},
            {"num": 13, "par": 4, "hcp": 8, "yds": 385, "tips": {"Scott": "Tricky green slopes—aim below pin.", "Troy": "Stroke hole—play for middle green.", "Allen": "Stroke hole—focus on lag putt."}},
            {"num": 14, "par": 3, "hcp": 16, "yds": 155, "tips": {"Scott": "Water left—miss right.", "Troy": "Solid par hole historically.", "Allen": "Favor right fringe."}},
            {"num": 15, "par": 4, "hcp": 4, "yds": 400, "tips": {"Scott": "Tough stretch hole—center fairway is key.", "Troy": "Stroke hole—use your stroke wisely.", "Allen": "Stroke hole—keep tempo smooth."}},
            {"num": 16, "par": 4, "hcp": 12, "yds": 365, "tips": {"Scott": "Short par 4—wedge distance approach.", "Troy": "You score well here—attack.", "Allen": "Stroke hole—good scoring hole."}},
            {"num": 17, "par": 5, "hcp": 6, "yds": 520, "tips": {"Scott": "Penultimate test—watch hazard right.", "Troy": "Stroke hole—stay in fairway.", "Allen": "Stroke hole—three steady shots."}},
            {"num": 18, "par": 4, "hcp": 14, "yds": 355, "tips": {"Scott": "Great finishing hole—aim at clubhouse line.", "Troy": "Finish strong—you historically score well.", "Allen": "Solid closing hole."}},
        ],
    },
    "Salt Pond (Black Tees)": {
        "rating": 58.2,
        "slope": 98,
        "par": 61,
        "holes": [
            {"num": 1, "par": 3, "hcp": 13, "yds": 145, "tips": {"Scott": "Quick start—smooth iron.", "Troy": "Good par chance.", "Allen": "Aim center green."}},
            {"num": 2, "par": 4, "hcp": 3, "yds": 280, "tips": {"Scott": "Short par 4—layup or drive green.", "Troy": "Stroke hole—play safe iron off tee.", "Allen": "Stroke hole—avoid front hazard."}},
            {"num": 3, "par": 3, "hcp": 17, "yds": 125, "tips": {"Scott": "Short iron—target pin.", "Troy": "High point yield hole.", "Allen": "Attack flag."}},
            {"num": 4, "par": 3, "hcp": 9, "yds": 155, "tips": {"Scott": "Watch wind off marsh.", "Troy": "Stroke hole—club up.", "Allen": "Stroke hole—smooth tempo."}},
            {"num": 5, "par": 4, "hcp": 1, "yds": 295, "tips": {"Scott": "HCP #1—narrow fairway, play smart.", "Troy": "Stroke hole—keep drive in play.", "Allen": "Stroke hole—play for bogey/par."}},
            {"num": 6, "par": 3, "hcp": 15, "yds": 135, "tips": {"Scott": "Short par 3—favor center.", "Troy": "You score well—be confident.", "Allen": "Good par opportunity."}},
            {"num": 7, "par": 3, "hcp": 7, "yds": 160, "tips": {"Scott": "Tricky wind—check tree tops.", "Troy": "Stroke hole—play for green center.", "Allen": "Stroke hole—aim middle."}},
            {"num": 8, "par": 4, "hcp": 5, "yds": 275, "tips": {"Scott": "Short par 4—birdie chance.", "Troy": "Stroke hole—aggressive layup.", "Allen": "Stroke hole—good scoring hole."}},
            {"num": 9, "par": 3, "hcp": 11, "yds": 150, "tips": {"Scott": "Solid front finish.", "Troy": "Smooth 7/8 iron.", "Allen": "Favor safe side."}},
            {"num": 10, "par": 3, "hcp": 14, "yds": 140, "tips": {"Scott": "Back 9 opener—clean contact.", "Troy": "Good point candidate.", "Allen": "Target middle green."}},
            {"num": 11, "par": 4, "hcp": 4, "yds": 285, "tips": {"Scott": "Tough green contour.", "Troy": "Stroke hole—don't overswing.", "Allen": "Stroke hole—keep it straight."}},
            {"num": 12, "par": 3, "hcp": 18, "yds": 115, "tips": {"Scott": "Easiest hole—wedge in hand.", "Troy": "High birdie rate.", "Allen": "Attack the pin."}},
            {"num": 13, "par": 3, "hcp": 8, "yds": 165, "tips": {"Scott": "Mid-iron test.", "Troy": "Stroke hole—favor center.", "Allen": "Stroke hole—smooth swing."}},
            {"num": 14, "par": 4, "hcp": 2, "yds": 290, "tips": {"Scott": "HCP #2—watch water right.", "Troy": "Stroke hole—bail left if needed.", "Allen": "Stroke hole—play safe."}},
            {"num": 15, "par": 3, "hcp": 16, "yds": 130, "tips": {"Scott": "Short hole—favor left pin.", "Troy": "You score well here.", "Allen": "Easy par setup."}},
            {"num": 16, "par": 3, "hcp": 10, "yds": 150, "tips": {"Scott": "Guard against short.", "Troy": "Stroke hole—take enough club.", "Allen": "Stroke hole—center green."}},
            {"num": 17, "par": 4, "hcp": 6, "yds": 270, "tips": {"Scott": "Drivable par 4—smart choice.", "Troy": "Stroke hole—layup sets up easy pitch.", "Allen": "Stroke hole—stay in fairway."}},
            {"num": 18, "par": 3, "hcp": 12, "yds": 145, "tips": {"Scott": "Closing par 3—finish strong.", "Troy": "Great historical finish.", "Allen": "Solid par chance."}},
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

import streamlit as st
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Walker Cup App", layout="centered")

SAVE_FILE = "wc_scores_backup.json"

# Page Title & Subtitle
st.markdown("<h4 style='margin-bottom:0px;'>⛳ Walker Cup Tournament</h4>", unsafe_allow_html=True)
st.caption("3-Player Extreme Points (XP2K4) Format")

# --- INITIALIZE PLAYERS & HANDICAPS IN SESSION STATE ---
if "p1_name" not in st.session_state:
    st.session_state.p1_name = "Player 1"
if "p1_hcp" not in st.session_state:
    st.session_state.p1_hcp = 0

if "p2_name" not in st.session_state:
    st.session_state.p2_name = "Player 2"
if "p2_hcp" not in st.session_state:
    st.session_state.p2_hcp = 0

if "p3_name" not in st.session_state:
    st.session_state.p3_name = "Player 3"
if "p3_hcp" not in st.session_state:
    st.session_state.p3_hcp = 0

p1 = st.session_state.p1_name
p1_hcp = st.session_state.p1_hcp
p2 = st.session_state.p2_name
p2_hcp = st.session_state.p2_hcp
p3 = st.session_state.p3_name
p3_hcp = st.session_state.p3_hcp

# --- DEFAULT 18-HOLE COURSE STRUCTURE ---
DEFAULT_COURSE_DATA = {
    "Hole": list(range(1, 19)),
    "Yards": [400] * 18,
    "Par": [4] * 18,
    "Hcp": list(range(1, 19))
}

# --- PERSISTENCE FUNCTIONS ---
def load_saved_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                saved_dict = json.load(f)
                return pd.DataFrame(saved_dict)
        except Exception:
            pass
    df_init = pd.DataFrame(DEFAULT_COURSE_DATA)
    df_init[p1] = 0
    df_init[p2] = 0
    df_init[p3] = 0
    return df_init

def save_data(df_to_save):
    with open(SAVE_FILE, "w") as f:
        json.dump(df_to_save.to_dict(), f)

if "score_data" not in st.session_state:
    st.session_state.score_data = load_saved_data()

df = st.session_state.score_data

# Ensure player columns stay synced if names change
if p1 not in df.columns or p2 not in df.columns or p3 not in df.columns:
    df.columns = ["Hole", "Yards", "Par", "Hcp", p1, p2, p3]

# --- CALCULATE 3-PLAYER WALKER CUP EXTREME POINTS ---
p1_pts = 0
p2_pts = 0
p3_pts = 0

for _, row in df.iterrows():
    h_hcp = int(row["Hcp"])
    g1 = int(row[p1])
    g2 = int(row[p2])
    g3 = int(row[p3])

    # Calculate net strokes per hole
    s1 = 1 if h_hcp <= p1_hcp else 0
    s2 = 1 if h_hcp <= p2_hcp else 0
    s3 = 1 if h_hcp <= p3_hcp else 0

    net1 = g1 - s1 if g1 > 0 else 0
    net2 = g2 - s2 if g2 > 0 else 0
    net3 = g3 - s3 if g3 > 0 else 0

    # Determine hole base value
    if h_hcp <= 6:
        win_val = 9
    elif h_hcp <= 12:
        win_val = 6
    else:
        win_val = 3

    # Award points when all 3 players have entered scores
    if g1 > 0 and g2 > 0 and g3 > 0:
        net_scores = {p1: net1, p2: net2, p3: net3}
        min_score = min(net_scores.values())
        winners = [player for player, score in net_scores.items() if score == min_score]

        if len(winners) == 1:
            # Lone winner gets full hole value
            if winners[0] == p1:
                p1_pts += win_val
            elif winners[0] == p2:
                p2_pts += win_val
            elif winners[0] == p3:
                p3_pts += win_val
        elif len(winners) == 2:
            # 2-way tie payouts: 3, 2, or 1 point each
            tie_payout = win_val // 3
            if p1 in winners:
                p1_pts += tie_payout
            if p2 in winners:
                p2_pts += tie_payout
            if p3 in winners:
                p3_pts += tie_payout
        elif len(winners) == 3:
            # 3-way tie payouts: 3, 2, or 1 point each
            tie_payout = win_val // 3
            p1_pts += tie_payout
            p2_pts += tie_payout
            p3_pts += tie_payout

# --- POINTS LEADERBOARD BOXES WITH LEADER HIGHLIGHT ---
max_pts = max(p1_pts, p2_pts, p3_pts)

style_default = "background-color: transparent; color: #FFFFFF; border: 1.5px solid #FFFFFF;"
style_leader = "background-color: #28A745; color: #000000; border: 1.5px solid #28A745;"

p1_style = style_leader if (p1_pts == max_pts and p1_pts > 0) else style_default
p2_style = style_leader if (p2_pts == max_pts and p2_pts > 0) else style_default
p3_style = style_leader if (p3_pts == max_pts and p3_pts > 0) else style_default

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 5px; margin-bottom: 5px;">
        <div style="width: 90px; border-radius: 6px; padding: 6px 0px; text-align: center; {p1_style}">
            <span style="font-size: 12px; font-weight: bold;">{p1}</span><br>
            <span style="font-size: 20px; font-weight: 800; line-height: 1.1;">{int(p1_pts)} PTS</span>
        </div>
        <div style="width: 90px; border-radius: 6px; padding: 6px 0px; text-align: center; {p2_style}">
            <span style="font-size: 12px; font-weight: bold;">{p2}</span><br>
            <span style="font-size: 20px; font-weight: 800; line-height: 1.1;">{int(p2_pts)} PTS</span>
        </div>
        <div style="width: 90px; border-radius: 6px; padding: 6px 0px; text-align: center; {p3_style}">
            <span style="font-size: 12px; font-weight: bold;">{p3}</span><br>
            <span style="font-size: 20px; font-weight: 800; line-height: 1.1;">{int(p3_pts)} PTS</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# --- HOLE SELECTOR ---
selected_hole = st.number_input("Select Hole Being Played", min_value=1, max_value=18, step=1, value=1)
hole_info = df[df["Hole"] == selected_hole].iloc[0]

hole_hcp = int(hole_info["Hcp"])
hole_par = int(hole_info["Par"])
hole_yards = int(hole_info["Yards"])

hole_pts = 9 if hole_hcp <= 6 else (6 if hole_hcp <= 12 else 3)
hole_pts_str = f"<span style='color: green; font-weight: bold;'>{hole_pts} PTS</span>"

st.markdown(
    f"##### Hole {selected_hole} | {hole_yards} Yds | Par {hole_par} | Hcp {hole_hcp} | {hole_pts_str}",
    unsafe_allow_html=True
)

st.write("")

curr_p1 = int(df.loc[df["Hole"] == selected_hole, p1].values[0])
curr_p2 = int(df.loc[df["Hole"] == selected_hole, p2].values[0])
curr_p3 = int(df.loc[df["Hole"] == selected_hole, p3].values[0])

# --- SCORE ENTRY FORM WITH SUBMIT BUTTON ---
with st.form(key=f"wc_hole_form_{selected_hole}"):
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        entered_p1 = st.number_input(f"{p1}", min_value=0, max_value=15, value=curr_p1, step=1)
    with s_col2:
        entered_p2 = st.number_input(f"{p2}", min_value=0, max_value=15, value=curr_p2, step=1)
    with s_col3:
        entered_p3 = st.number_input(f"{p3}", min_value=0, max_value=15, value=curr_p3, step=1)
    
    submit_hole = st.form_submit_button("✅ Save Score for Hole", use_container_width=True)

if submit_hole:
    df.loc[df["Hole"] == selected_hole, p1] = entered_p1
    df.loc[df["Hole"] == selected_hole, p2] = entered_p2
    df.loc[df["Hole"] == selected_hole, p3] = entered_p3
    st.session_state.score_data = df
    save_data(df)
    st.success(f"Hole {selected_hole} scores saved!")
    st.rerun()

st.divider()

# --- CHECK FOR 18-HOLE COMPLETION & EXCEL DOWNLOAD ---
completed_holes = df[(df[p1] > 0) & (df[p2] > 0) & (df[p3] > 0)]
all_18_done = len(completed_holes) == 18

if all_18_done:
    st.balloons()
    st.success("🎉 Walker Cup Match Completed!")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Walker Cup Match")
    
    excel_data = buffer.getvalue()
    
    st.download_button(
        label="📥 Download Final Match Spreadsheet (.xlsx)",
        data=excel_data,
        file_name="walker_cup_final_scorecard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.divider()

# --- ALWAYS-VISIBLE HORIZONTAL SCORECARD TABLE ---
hole_cells = ""
pts_cells = ""
p1_cells = ""
p2_cells = ""
p3_cells = ""

green_style = "background-color: #28A745; color: #000000; padding: 2px 4px; border-radius: 3px; font-weight: bold; font-size: 13px;"
yellow_style = "background-color: #FFC107; color: #000000; padding: 2px 4px; border-radius: 3px; font-weight: bold; font-size: 13px;"

for _, row in df.iterrows():
    h = int(row["Hole"])
    hcp = int(row["Hcp"])
    g1 = int(row[p1])
    g2 = int(row[p2])
    g3 = int(row[p3])

    s1 = 1 if hcp <= p1_hcp else 0
    s2 = 1 if hcp <= p2_hcp else 0
    s3 = 1 if hcp <= p3_hcp else 0

    hole_pts = 9 if hcp <= 6 else (6 if hcp <= 12 else 3)

    p1_dot = "<span style='color:#FF4B4B; font-size:9px;'>●</span>" if s1 > 0 else ""
    p2_dot = "<span style='color:#FF4B4B; font-size:9px;'>●</span>" if s2 > 0 else ""
    p3_dot = "<span style='color:#FF4B4B; font-size:9px;'>●</span>" if s3 > 0 else ""

    p1_val_str = f"{g1}{p1_dot}" if g1 > 0 else "-"
    p2_val_str = f"{g2}{p2_dot}" if g2 > 0 else "-"
    p3_val_str = f"{g3}{p3_dot}" if g3 > 0 else "-"

    p1_formatted = f"<span style='font-size:13px; font-weight:bold;'>{p1_val_str}</span>"
    p2_formatted = f"<span style='font-size:13px; font-weight:bold;'>{p2_val_str}</span>"
    p3_formatted = f"<span style='font-size:13px; font-weight:bold;'>{p3_val_str}</span>"

    if g1 > 0 and g2 > 0 and g3 > 0:
        net1 = g1 - s1
        net2 = g2 - s2
        net3 = g3 - s3

        net_dict = {p1: net1, p2: net2, p3: net3}
        min_net = min(net_dict.values())
        winners = [player for player, score in net_dict.items() if score == min_net]

        style_to_apply = green_style if len(winners) == 1 else yellow_style

        if p1 in winners:
            p1_formatted = f"<span style='{style_to_apply}'>{p1_val_str}</span>"
        if p2 in winners:
            p2_formatted = f"<span style='{style_to_apply}'>{p2_val_str}</span>"
        if p3 in winners:
            p3_formatted = f"<span style='{style_to_apply}'>{p3_val_str}</span>"

    hole_cells += f"<td>{h}</td>"
    pts_cells += f"<td>{hole_pts}</td>"
    p1_cells += f"<td>{p1_formatted}</td>"
    p2_cells += f"<td>{p2_formatted}</td>"
    p3_cells += f"<td>{p3_formatted}</td>"

horizontal_table_code = f"""
<style>
    .horizontal-scorecard-container {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 5px;
    }}
    .horizontal-scorecard {{
        border-collapse: collapse;
        font-family: sans-serif;
        white-space: nowrap;
        margin: 0 auto;
    }}
    .horizontal-scorecard th {{
        text-align: center !important;
        padding: 6px 8px;
        border-bottom: 2px solid #666;
        border-right: 1px solid #444;
        font-size: 12px;
        background-color: #262730;
        position: sticky;
        left: 0;
        z-index: 2;
    }}
    .horizontal-scorecard td {{
        text-align: center !important;
        padding: 6px 8px;
        border-bottom: 1px solid #444;
        border-right: 1px solid #333;
        font-size: 12px;
        min-width: 32px;
    }}
</style>
<div class="horizontal-scorecard-container">
    <table class="horizontal-scorecard">
        <tbody>
            <tr>
                <th>Hole</th>
                {hole_cells}
            </tr>
            <tr>
                <th>Points</th>
                {pts_cells}
            </tr>
            <tr>
                <th>{p1}</th>
                {p1_cells}
            </tr>
            <tr>
                <th>{p2}</th>
                {p2_cells}
            </tr>
            <tr>
                <th>{p3}</th>
                {p3_cells}
            </tr>
        </tbody>
    </table>
</div>
"""

st.html(horizontal_table_code)

st.divider()

# --- RESET ROUND BUTTON & PLAYER SETUP ---
b_col1, b_col2 = st.columns(2)
with b_col1:
    if st.button("🔄 Reset Round Scores", use_container_width=True):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        df_reset = pd.DataFrame(DEFAULT_COURSE_DATA)
        df_reset[p1] = 0
        df_reset[p2] = 0
        df_reset[p3] = 0
        st.session_state.score_data = df_reset
        st.rerun()

with st.expander("⚙️ Player Setup & Handicaps", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_p1_name = st.text_input("Player 1 Name", value=p1)
        new_p1_hcp = st.number_input(f"{new_p1_name} Hcp", value=p1_hcp, min_value=0, max_value=36, step=1)
    with col2:
        new_p2_name = st.text_input("Player 2 Name", value=p2)
        new_p2_hcp = st.number_input(f"{new_p2_name} Hcp", value=p2_hcp, min_value=0, max_value=36, step=1)
    with col3:
        new_p3_name = st.text_input("Player 3 Name", value=p3)
        new_p3_hcp = st.number_input(f"{new_p3_name} Hcp", value=p3_hcp, min_value=0, max_value=36, step=1)

    if (new_p1_name != p1 or new_p2_name != p2 or new_p3_name != p3 or 
        new_p1_hcp != p1_hcp or new_p2_hcp != p2_hcp or new_p3_hcp != p3_hcp):
        st.session_state.p1_name = new_p1_name
        st.session_state.p1_hcp = new_p1_hcp
        st.session_state.p2_name = new_p2_name
        st.session_state.p2_hcp = new_p2_hcp
        st.session_state.p3_name = new_p3_name
        st.session_state.p3_hcp = new_p3_hcp
        st.rerun()

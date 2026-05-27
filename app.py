import streamlit as st
import pandas as pd
import time
import datetime

# Set web page configuration with Capgemini-inspired theme colors
st.set_page_config(
    page_title="AI Delivery Lab - CTF Scoreboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via CSS
st.markdown("""
    <style>
    .main-header { font-size:42px !important; font-weight: 700; color: #0070AD; margin-bottom: 5px; }
    .sub-header { font-size:20px !important; color: #5A6B7C; margin-bottom: 25px; }
    .metric-card { background-color: #F4F7FA; border-left: 5px solid #0070AD; padding: 15px; border-radius: 4px; }
    .facilitator-box { background-color: #FFF9E6; border: 1px solid #FFE0B2; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #F0F2F5; border-radius: 4px 4px 0px 0px; padding: 10px 20px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #0070AD !important; color: white !important; }
    </style>
""", unsafe_unsafe_override_html=True)

# -----------------------------------------------------------------------------
# GLOBAL IN-MEMORY DATABASE STRUCTURE (Shared across all user sessions)
# -----------------------------------------------------------------------------
class CTFDatabase:
    def __init__(self):
        self.start_time = time.time()
        self.logs = []
        
        # Hardcode the 10 Rooms exactly based on the Framework
        self.rooms = {}
        for i in range(1, 11):
            room_name = f"Room {i}"
            if i <= 4:
                track = "Coding with Anthropic"
                mission = "Mission 1: Industrialize the Code"
                flag_codes = ["FLAG-PROMPT_MASTER", "FLAG-SEE_THE_HIDDEN", "FLAG-CLEAN_CODE", "FLAG-INDUSTRIALIZE_CODE"]
            elif i <= 7:
                track = "Agentic with n8n"
                mission = "Mission 2: Automate the Ops Loop"
                flag_codes = ["FLAG-WORKFLOW_READY", "FLAG-ROUTE_SMART", "FLAG-AUTOMATE_BETTER", "FLAG-SCALE_AI"]
            else:
                track = "Office Assistant (OpenAI)"
                mission = "Mission 3: Build the Smart Office Assistant"
                flag_codes = ["FLAG-KNOWLEDGE_POWER", "FLAG-TRUST_AI", "FLAG-ACTION_DRIVEN", "FLAG-AI_ASSISTANT_SCALE"]
                
            self.rooms[room_name] = {
                "room": room_name,
                "track": track,
                "mission": mission,
                "points": 0,
                "flags": {
                    "Flag 1": {"name": "Flag 1", "target_code": flag_codes[0], "status": "Locked", "points": 100, "timestamp": None},
                    "Flag 2": {"name": "Flag 2", "target_code": flag_codes[1], "status": "Locked", "points": 200, "timestamp": None},
                    "Flag 3": {"name": "Flag 3", "target_code": flag_codes[2], "status": "Locked", "points": 300, "timestamp": None},
                    "Flag 4": {"name": "Flag 4", "target_code": flag_codes[3], "status": "Locked", "points": 300, "timestamp": None},
                },
                "bonuses": {
                    "Clear Explanation (+50)": False,
                    "Strong Collaboration (+50)": False,
                    "Industrialization Bonus (+100)": False
                },
                "hints": {
                    "Hint 1 (Free)": {"unlocked": False, "text": self.get_hint_text(track, 1)},
                    "Hint 2 (Free)": {"unlocked": False, "text": self.get_hint_text(track, 2)},
                    "Hint 3 (Final -50 Pts)": {"unlocked": False, "text": self.get_hint_text(track, 3)}
                },
                "advanced_flags_count": 0,
                "industrialization_bonus_points": 0,
                "completion_time_str": "N/A",
                "completion_timestamp": None
            }
            
        self.add_log("System", "CTF Dashboard Initialized successfully for 10 Rooms.")

    def get_hint_text(self, track, hint_num):
        hints = {
            "Coding with Anthropic": {
                1: "Structure your prompt to ask for valid JSON format and explicitly define fields like 'priority' and 'reason'.",
                2: "For the hidden clue, look closely into the provided broken code comments for a line containing '# asset_code ='.",
                3: "To win the Industrialization Flag, define a clear user persona (e.g., Delivery Manager) and state how much time this saves per week."
            },
            "Agentic with n8n": {
                1: "Ensure that your input node runs successfully and passes a valid JSON ticket to the classification node.",
                2: "Verify your routing using a ticket containing 'server down' - it should automatically route to the urgent operations queue.",
                3: "To simplify the workflow, merge redundant evaluation conditions and group similar routing decision buckets together."
            },
            "Office Assistant (OpenAI)": {
                1: "Explicitly append the constraint text: 'Answer using only the provided documents' to your prompt structure.",
                2: "To beat the hallucination trap, instruct the model: 'If the answer is not found, state exactly: Not found in documents'.",
                3: "Your structured output must include a clear, plain-English summary table followed by an operational bulleted list of actions."
            }
        }
        return hints[track][hint_num]

    def add_log(self, scope, text):
        t_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.insert(0, f"[{t_str}] ({scope}) {text}")

    def recalculate_score(self, room_name):
        room = self.rooms[room_name]
        total = 0
        adv_count = 0
        indus_pts = 0
        all_done = True
        last_timestamp = None
        
        for f_idx, f_info in room["flags"].items():
            if f_info["status"] == "Approved":
                total += f_info["points"]
                if f_idx in ["Flag 3", "Flag 4"]:
                    adv_count += 1
                if f_info["timestamp"]:
                    if last_timestamp is None or f_info["timestamp"] > last_timestamp:
                        last_timestamp = f_info["timestamp"]
            else:
                all_done = False
                
        if room["bonuses"]["Clear Explanation (+50)"]: total += 50
        if room["bonuses"]["Strong Collaboration (+50)"]: total += 50
        if room["bonuses"]["Industrialization Bonus (+100)"]: 
            total += 100
            indus_pts += 100
            
        if room["hints"]["Hint 3 (Final -50 Pts)"]["unlocked"]:
            total -= 50
            
        room["points"] = max(0, total)
        room["advanced_flags_count"] = adv_count
        room["industrialization_bonus_points"] = indus_pts
        
        if all_done and room["completion_timestamp"] is None:
            room["completion_timestamp"] = last_timestamp if last_timestamp else (time.time() - self.start_time)
            mins = int(room["completion_timestamp"] // 60)
            secs = int(room["completion_timestamp"] % 60)
            room["completion_time_str"] = f"{mins}m {secs}s"

    def get_sorted_leaderboard(self):
        def sort_key(item):
            r_data = item[1]
            # Tie-breakers: 1. Points (Desc), 2. Advanced Flags (Desc), 3. Industrialization Bonus (Desc), 4. Completion Time (Asc)
            ctime = r_data["completion_timestamp"] if r_data["completion_timestamp"] is not None else float('inf')
            return (-r_data["points"], -r_data["advanced_flags_count"], -r_data["industrialization_bonus_points"], ctime)
        return sorted(self.rooms.items(), key=sort_key)

# Initialize the global shared database across user connections
@st.cache_resource
def get_shared_db():
    return CTFDatabase()

db = get_shared_db()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & TIMER DISPLAY
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/clouds/100/artificial-intelligence.png", width=70)
st.sidebar.title("CTF Control Center")
st.sidebar.markdown("---")

# Event Info Panel
st.sidebar.markdown("### 📅 Live Session Status")
st.sidebar.info("**Event:** AI Delivery Lab\n\n**Format:** Onsite (90 Pax)\n\n**Duration:** 3 Hours / 10 Rooms")

# -----------------------------------------------------------------------------
# INTERFACE TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Live Leaderboard", 
    "🎯 Participant Submission Desk", 
    "🔐 Facilitator Validation Desk", 
    "📋 Event Framework & Cheat Sheets"
])

# -----------------------------------------------------------------------------
# TAB 1: LIVE LEADERBOARD (Auto-Calculates and Applies Tie-Breakers)
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("<div class='main-header'>AI Delivery Lab Leaderboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Real-time standing and score trackings of all 10 project rooms</div>", unsafe_allow_html=True)
    
    leaderboard_data = db.get_sorted_leaderboard()
    
    # Showcase top 3 Podium Teams visually
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card' style='border-left-color:#FFD700;'>🥇 **Rank 1: {leaderboard_data[0][0]}**<br><span style='font-size:24px; font-weight:700;'>{leaderboard_data[0][1]['points']} Pts</span><br><small>{leaderboard_data[0][1]['track']}</small></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card' style='border-left-color:#C0C0C0;'>🥈 **Rank 2: {leaderboard_data[1][0]}**<br><span style='font-size:24px; font-weight:700;'>{leaderboard_data[1][1]['points']} Pts</span><br><small>{leaderboard_data[1][1]['track']}</small></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card' style='border-left-color:#CD7F32;'>🥉 **Rank 3: {leaderboard_data[2][0]}**<br><span style='font-size:24px; font-weight:700;'>{leaderboard_data[2][1]['points']} Pts</span><br><small>{leaderboard_data[2][1]['track']}</small></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Compile table format data
    rows = []
    for idx, (r_name, r_data) in enumerate(leaderboard_data):
        flags_captured = [f_name for f_name, f_val in r_data["flags"].items() if f_val["status"] == "Approved"]
        flags_str = ", ".join(flags_captured) if flags_captured else "None"
        
        bonus_list = []
        if r_data["bonuses"]["Clear Explanation (+50)"]: bonus_list.append("Explanation")
        if r_data["bonuses"]["Strong Collaboration (+50)"]: bonus_list.append("Collaboration")
        if r_data["bonuses"]["Industrialization Bonus (+100)"]: bonus_list.append("Industrialization")
        bonuses_str = ", ".join(bonus_list) if bonus_list else "None"
        
        hints_count = sum(1 for h in r_data["hints"].values() if h["unlocked"])
        
        rows.append({
            "Rank": idx + 1,
            "Room Name": r_name,
            "Assigned Track": r_data["track"],
            "Total Score": r_data["points"],
            "Flags Approved": flags_str,
            "Advanced Flags Count": r_data["advanced_flags_count"],
            "Bonuses Earned": bonuses_str,
            "Hints Requested": hints_count,
            "Validated Completion Time": r_data["completion_time_str"]
        })
        
    df_lb = pd.DataFrame(rows)
    st.dataframe(df_lb, use_container_width=True, hide_index=True)

    # Real-time Bar Chart visualization of scores
    st.markdown("### 📊 Points Distribution Chart")
    chart_df = pd.DataFrame({
        "Room": [r[0] for r in leaderboard_data],
        "Points": [r[1]["points"] for r in leaderboard_data]
    })
    st.bar_chart(chart_df, x="Room", y="Points", color="#0070AD")

# -----------------------------------------------------------------------------
# TAB 2: PARTICIPANT DASHBOARD (For Room Members to Request Hints & Submit Flags)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("<div class='main-header'>Participant Submission Portal</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Select your assigned project room to view instructions, manage hints, and unlock mission flags</div>", unsafe_allow_html=True)
    
    selected_room = st.selectbox("🎯 Select Your Active Room Number:", list(db.rooms.keys()))
    room_data = db.rooms[selected_room]
    
    # Display Room Summary Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(f"**Assigned Lab Track:**\n\n{room_data['track']}")
    with c2:
        st.warning(f"**Current Lab Mission:**\n\n{room_data['mission']}")
    with c3:
        st.success(f"**Total Room Points Earned:**\n\n💰 {room_data['points']} Points")
        
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📦 Submit Found Flag String")
        st.write("When your team extracts or derives a Flag String, paste it exactly below to request facilitator validation:")
        
        input_code = st.text_input("Enter Flag Code String (e.g., FLAG-PROMPT_MASTER):", key="flag_input_box").strip()
        
        if st.button("🚀 Submit Flag for Facilitator Review", use_container_width=True):
            if not input_code:
                st.error("Submission error: Code field cannot be blank.")
            else:
                match_found = False
                for f_idx, f_info in room_data["flags"].items():
                    if f_info["target_code"] == input_code:
                        match_found = True
                        if f_info["status"] == "Approved":
                            st.info("This flag has already been successfully approved and credited by your facilitator.")
                        elif f_info["status"] == "Pending Facilitator Review":
                            st.warning("This flag is already waiting in the validation queue. Please alert your Room Facilitator to grade it.")
                        else:
                            f_info["status"] = "Pending Facilitator Review"
                            db.add_log(selected_room, f"Submitted correct code string for {f_idx}. Awaiting facilitator validation.")
                            st.success(f"🎉 Correct flag string recognized! {f_idx} status set to 'Pending Facilitator Review'. Call your room facilitator over to prove your logic and unlock your points!")
                            st.rerun()
                        break
                if not match_found:
                    st.error("❌ Invalid Flag Code String. Check your syntax, remove any extra spaces, and make sure it is in full uppercase.")
                    db.add_log(selected_room, f"Failed flag code submission attempt: '{input_code}'")
                    
        # List of Flags and current live statuses
        st.markdown("<br>### 📋 Your Room's Flag Progress Status", unsafe_allow_html=True)
        for f_idx, f_info in room_data["flags"].items():
            if f_info["status"] == "Approved":
                st.markdown(f"✅ **{f_idx}** ({f_info['points']} Pts) — **APPROVED & SCORE CREDITED**")
            elif f_info["status"] == "Pending Facilitator Review":
                st.markdown(f"⏳ **{f_idx}** ({f_info['points']} Pts) — **AWAITING FACILITATOR VALIDATION (Call them over!)**")
            else:
                st.markdown(f"🔒 **{f_idx}** ({f_info['points']} Pts) — **LOCKED**")

    with col_right:
        st.markdown("### 💡 Interactive Hints Hub")
        st.caption("Each room gets 2 free hints per track. Unlocking the 3rd/Final hint incurs an immediate -50 point penalty deduction.")
        
        for h_name, h_info in room_data["hints"].items():
            if h_info["unlocked"]:
                st.info(f"**{h_name}:**\n\n{h_info['text']}")
            else:
                if st.button(f"🔓 Reveal {h_name}", key=f"btn_{selected_room}_{h_name}"):
                    h_info["unlocked"] = True
                    db.recalculate_score(selected_room)
                    db.add_log(selected_room, f"Unlocked {h_name}")
                    st.success(f"Hint unlocked successfully!")
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: FACILITATOR DESK (Allows Room Partners to Validate and Award Bonuses)
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("<div class='main-header'>Facilitator Validation Desk</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Secure environment for lab leads to approve flags, unlock hints, and distribute skill bonus points</div>", unsafe_allow_html=True)
    
    # Secure access point
    fac_password = st.text_input("🔑 Enter Access Credential Passkey:", type="password")
    if fac_password == "capgemini2026":
        st.success("Authorization granted. Welcome back, Lab Lead.")
        
        st.markdown("---")
        st.markdown("### 🚨 Pending Room Flag Approvals Queue")
        
        pending_count = 0
        for r_name, r_data in db.rooms.items():
            for f_idx, f_info in r_data["flags"].items():
                if f_info["status"] == "Pending Facilitator Review":
                    pending_count += 1
                    st.markdown(f"<div class='facilitator-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### 🚪 {r_name} ({r_data['track']}) — Requesting Approval for **{f_idx}**")
                    st.markdown(f"**Submitted Flag String:** `{f_info['target_code']}`")
                    
                    # Display the exact Cheat Sheet Checklist dynamically based on the specific Flag requested
                    st.markdown("**📋 Mandatory Facilitator Validation Checklist:**")
                    if r_data["track"] == "Coding with Anthropic":
                        if f_idx == "Flag 1":
                            st.markdown("- [ ] Team showed an improved, highly structured prompt template.\n- [ ] Output includes clear classification severity data inside a clean structured JSON/table layout.")
                        elif f_idx == "Flag 2":
                            st.markdown("- [ ] Team explicitly referenced the image file asset (`trace_hint.png`).\n- [ ] Team clearly demonstrates the specific hidden code comment route where the flag string was extracted.")
                        elif f_idx == "Flag 3":
                            st.markdown("- [ ] Refactored code contains at least 1 function structure with clear inputs/outputs.\n- [ ] Code is completely clean and modular (not just a basic print loop logic block).")
                        elif f_idx == "Flag 4":
                            st.markdown("- [ ] Team explains in plain English: What the asset is, Who would use it, and What exact delivery value it creates.")
                    elif r_data["track"] == "Agentic with n8n":
                        if f_idx == "Flag 1":
                            st.markdown("- [ ] Team shows a functional visual flow sequence sequence (Input → Process → Output Node).\n- [ ] A sample ticket passes completely through returning an accurate queue destination text label.")
                        elif f_idx == "Flag 2":
                            st.markdown("- [ ] Ask team: *'Where does server down route?'* (Correct: Operations/Urgent).\n- [ ] Verify that at least 3 out of 4 branch paths function perfectly.")
                        elif f_idx == "Flag 3":
                            st.markdown("- [ ] Team successfully reduced overall steps compared to the original intentionally overcomplicated workflow layout.\n- [ ] Process logic path is visually clean, highly optimized, and runs error-free.")
                        elif f_idx == "Flag 4":
                            st.markdown("- [ ] Team provides a compelling 60-second scaling pitch explaining reuse value and measurable operational KPIs.")
                    elif r_data["track"] == "Office Assistant (OpenAI)":
                        if f_idx == "Flag 1":
                            st.markdown("- [ ] System response successfully references factual material embedded within the official document packs.\n- [ ] Team demonstrates explicit source mapping/citations matching the underlying text files.")
                        elif f_idx == "Flag 2":
                            st.markdown("- [ ] Team identifies what information the ungrounded model originally invented.\n- [ ] Team shows strict prompt guardrails forcing the assistant to respond with 'Not found' when document facts are omitted.")
                        elif f_idx == "Flag 3":
                            st.markdown("- [ ] Output is neatly split into a concise technical summary block followed by actionable role-based items.\n- [ ] Language is tailored for the intended context (e.g., HR, Project Management Office).")
                        elif f_idx == "Flag 4":
                            st.markdown("- [ ] Team articulates a business story explaining who uses the tool and how it protects consistency and drops manual efforts.")
                    
                    # Approval Buttons
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        if st.button(f"✅ Approve & Credit Flag", key=f"app_{r_name}_{f_idx}", use_container_width=True):
                            f_info["status"] = "Approved"
                            f_info["timestamp"] = time.time() - db.start_time
                            db.recalculate_score(r_name)
                            db.add_log("Facilitator", f"APPROVED {f_idx} for {r_name}")
                            st.rerun()
                    with b_col2:
                        if st.button(f"❌ Reject Submission", key=f"rej_{r_name}_{f_idx}", use_container_width=True):
                            f_info["status"] = "Locked"
                            db.add_log("Facilitator", f"REJECTED {f_idx} submission for {r_name}")
                            st.rerun()
                            
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        if pending_count == 0:
            st.info("No flag submissions are currently awaiting validation in the queue. Teams are currently iterating.")
            
        st.markdown("---")
        st.markdown("### 🏅 Manage Bonuses & Manual Adjustments per Room")
        
        fac_room = st.selectbox("Select Target Room to Adjust:", list(db.rooms.keys()), key="fac_room_box")
        f_room_data = db.rooms[fac_room]
        
        st.markdown(f"**Current Status for {fac_room}:** Score: {f_room_data['points']} Pts | Track: {f_room_data['track']}")
        
        # Checkbox controls for individual room bonuses
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            exp_bonus = st.checkbox("Clear Explanation Bonus (+50)", value=f_room_data["bonuses"]["Clear Explanation (+50)"])
        with col_b2:
            col_bonus = st.checkbox("Strong Collaboration Bonus (+50)", value=f_room_data["bonuses"]["Strong Collaboration (+50)"])
        with col_b3:
            ind_bonus = st.checkbox("Industrialization Bonus (+100)", value=f_room_data["bonuses"]["Industrialization Bonus (+100)"])
            
        if st.button(f"💾 Save Adjustments for {fac_room}", use_container_width=True):
            f_room_data["bonuses"]["Clear Explanation (+50)"] = exp_bonus
            f_room_data["bonuses"]["Strong Collaboration (+50)"] = col_bonus
            f_room_data["bonuses"]["Industrialization Bonus (+100)"] = ind_bonus
            db.recalculate_score(fac_room)
            db.add_log("Facilitator", f"Updated skill bonus configurations for {fac_room}.")
            st.success(f"Successfully updated bonus states for {fac_room}!")
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 🪵 Live Action Activity Logs")
        st.text_area("Live Event Stream Log Entries:", value="\n".join(db.logs), height=250, disabled=True)
        
    elif fac_password:
        st.error("Access denied: Invalid passkey token entered.")

# -----------------------------------------------------------------------------
# TAB 4: SYSTEM INFO, AGENDA RUNBOOK & FACILITATOR SCRIPT CHEAT SHEETS
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("<div class='main-header'>Event Architecture & Cheat Sheets</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Complete timeline models, grading procedures, and participant configurations</div>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        ### ⏱️ Session Timeline Framework (3 Hours)
        * **0:00–0:15** | Kickoff + Challenge Rules Presentation + Role Mapping 
        * **0:15–0:25** | Workspace Onboarding & Challenge Lab Briefings
        * **0:25–1:45** | Active Challenge Execution (Unlocking Flags 1, 2 & 3)
        * **1:45–2:20** | Stretch Flag Sprint + Industrialization Value Wraps
        * **2:20–2:50** | Facilitator Review Desk Validations & Live Demos [cite: 4928]
        * **2:50–3:00** | Proclamation of Winners + Executive Key Takeaway Synthesis
        
        ### 👥 Mixed-Audience Role Assignments (5-6 Pax per Team)
        To ensure technical and non-technical participants contribute equally, ensure teams assign: [cite: 5200]
        1. **Prompt Lead** – Crafts, tests, and refines system instruction prompts.
        2. **Builder** – Manages software script execution, workflow nodes, and tools.
        3. **Investigator** – uncovers code comments, files, and image-based hints.
        4. **Business Translator** – Translates technical workflows into enterprise value.
        5. **Quality Checker** – Validates outputs against strict error criteria.
        """)
    
    with col_b:
        st.markdown("""
        ### ⚖️ Master Scoring Metric System
        * **Easy Flag (Flag 1):** `100 Points` [cite: 4526, 4652, 4668]
        * **Medium Flag (Flag 2):** `200 Points` [cite: 4546, 4668]
        * **Advanced Flag (Flag 3):** `300 Points` [cite: 4593]
        * **Stretch Industrialization Flag (Flag 4):** `300 Points` [cite: 4593]
        * **Explanation/Collaboration Bonuses:** `+50 Points Each`
        * **Industrialization High-Performer Bonus:** `+100 Points` [cite: 4593, 5038, 5102, 5172]
        * **Hint Penalties:** First 2 free per room, Final hint triggers `-50 Points`. [cite: 4947, 4948]
        
        ### 🧠 Strategic Facilitator Behavioral Code
        * **Encourage:** Collaboration, rapid prompt testing, process simplification. [cite: 5185, 5186, 5187, 5188]
        * **Say Things Like:** *"Make your prompt more specific"*, *"What is the absolute simplest version of this flow?"*, *"How could another project team reuse this code asset?"* [cite: 5190, 5191, 5192]
        * **Strictly Avoid:** Providing direct answers, writing the code for them, or accepting guesses. [cite: 4943, 4950, 5194, 5195]
        """)

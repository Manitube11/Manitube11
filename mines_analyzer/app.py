import streamlit as st
import logic

# Page Configuration
st.set_page_config(page_title="Mines Analyzer AI", layout="wide")

# Initialize Session State
if 'revealed_indices' not in st.session_state:
    st.session_state.revealed_indices = []
if 'history_indices' not in st.session_state:
    st.session_state.history_indices = []
if 'mines_count' not in st.session_state:
    st.session_state.mines_count = 3
if 'suggestion' not in st.session_state:
    st.session_state.suggestion = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'play' # 'play' or 'record_history'

# Custom CSS for RTL and Dark Theme tweaks
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', sans-serif;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .safe-tile {
        background-color: #2ecc71 !important;
        color: white !important;
    }
    .mine-tile {
        background-color: #e74c3c !important;
        color: white !important;
    }
    .suggested-tile {
        background-color: #f1c40f !important; # Yellow
        color: black !important;
        border: 2px solid white !important;
    }
    /* Stats Card Styling */
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4facfe;
    }
    .metric-label {
        font-size: 14px;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ تنظیمات (Settings)")
    st.session_state.mines_count = st.slider(
        "تعداد بمب‌ها (Number of Mines)",
        min_value=1, max_value=24, value=st.session_state.mines_count
    )

    if st.button("🔄 بازی جدید (Reset Game)"):
        st.session_state.revealed_indices = []
        st.session_state.suggestion = None
        st.session_state.mode = 'play'
        st.rerun()

    st.markdown("---")
    st.write("### تاریخچه بمب‌ها (Mine History)")
    st.write(f"تعداد ثبت شده: {len(st.session_state.history_indices)}")
    if st.button("🗑️ پاک کردن تاریخچه (Clear History)"):
        st.session_state.history_indices = []
        st.rerun()

# Main Content
st.title("💎 Mines Analyzer AI")

# Stats Section
col1, col2, col3 = st.columns(3)

# Calculate Stats
revealed_count = len(st.session_state.revealed_indices)
prob_next = logic.calculate_next_safe_probability(revealed_count, st.session_state.mines_count)
multiplier = logic.calculate_multiplier(revealed_count, st.session_state.mines_count)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">تعداد خانه‌های باز شده</div>
        <div class="metric-value">{revealed_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">احتمال امن بودن بعدی</div>
        <div class="metric-value">{prob_next:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">ضریب تئوری (Multiplier)</div>
        <div class="metric-value">{multiplier}x</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Grid Logic
def handle_click(index):
    if st.session_state.mode == 'play':
        if index not in st.session_state.revealed_indices:
            st.session_state.revealed_indices.append(index)
            # Reset suggestion if user picked it (or picked something else)
            st.session_state.suggestion = None
    elif st.session_state.mode == 'record_history':
        # Toggle mine in history
        st.session_state.history_indices.append(index)

# Suggestion Logic
if st.button("✨ پیشنهاد حرکت (AI Suggestion)", type="primary"):
    suggestion = logic.suggest_tile(
        st.session_state.revealed_indices,
        st.session_state.history_indices,
        strategy="avoid_recent" # Default to avoiding recent mines
    )
    st.session_state.suggestion = suggestion

# Mode Toggle
if st.session_state.mode == 'play':
    if st.button("📝 ثبت موقعیت بمب‌ها (بعد از باخت)", help="Record where mines were located"):
        st.session_state.mode = 'record_history'
        st.rerun()
else:
    st.info("⚠️ در حال ثبت موقعیت بمب‌ها. روی خانه‌هایی که بمب بودند کلیک کنید.")
    if st.button("✅ پایان ثبت (بازگشت به بازی)"):
        st.session_state.mode = 'play'
        st.session_state.revealed_indices = [] # Reset for new game
        st.session_state.suggestion = None
        st.rerun()

# Render Grid
# We use a 5x5 grid of columns
grid_container = st.container()

with grid_container:
    for row in range(5):
        cols = st.columns(5)
        for col in range(5):
            index = row * 5 + col

            # Determine button style/label based on state
            label = "💎"
            disabled = False
            is_revealed = index in st.session_state.revealed_indices
            is_suggested = (index == st.session_state.suggestion)
            is_history = (index in st.session_state.history_indices and st.session_state.mode == 'record_history') # Just visual indicator? No, history accumulates.

            # Visual Logic
            if st.session_state.mode == 'play':
                if is_revealed:
                    label = "💎" # Revealed safe
                    disabled = True
                elif is_suggested:
                    label = "❓" # Suggestion
                else:
                    label = " " # Unrevealed
            else: # Record Mode
                # Show mines history temporarily as "💣" for this session input?
                # Actually, let's just show what we are adding.
                # Since history accumulates, we might want to just show the ones added *now*?
                # For simplicity, clicking adds to history.
                label = "💣"

            # Create button
            # We use a unique key for each button
            if cols[col].button(label, key=f"btn_{index}", disabled=disabled and st.session_state.mode == 'play', on_click=handle_click, args=(index,)):
                pass

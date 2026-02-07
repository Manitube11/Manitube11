import streamlit as st
import plotly.graph_objects as go
from mines_analyzer.logic import MineAnalyzer, calculate_next_safe_probability, calculate_multiplier

# --- Page Config ---
st.set_page_config(page_title="Mines Analyzer AI v2", layout="wide", page_icon="💣")

# --- Custom CSS for RTL & Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 24px;
        border-radius: 12px;
        border: 2px solid #333;
        background-color: #262730;
        color: white;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        transform: scale(1.02);
    }
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        text-align: center;
        color: #aaa;
    }
    div[data-testid="stMetricValue"] {
        text-align: center;
        color: #4facfe;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = MineAnalyzer()

if 'revealed' not in st.session_state:
    st.session_state.revealed = set() # Set of indices

if 'current_suggestion' not in st.session_state:
    st.session_state.current_suggestion = None

if 'mode' not in st.session_state:
    st.session_state.mode = 'play' # 'play', 'input_mines'

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ تنظیمات (Settings)")

    mines_count = st.slider("تعداد بمب‌ها (Mines)", 1, 24, 3)

    st.divider()

    st.subheader("🧠 استراتژی تحلیل (Strategy)")
    strategy = st.radio(
        "انتخاب استراتژی:",
        ("conservative", "balanced", "aggressive"),
        format_func=lambda x: {
            "conservative": "🛡️ محافظه‌کار (Conservative) - دوری از نقاط داغ",
            "balanced": "⚖️ متعادل (Balanced) - ترکیبی",
            "aggressive": "🔥 تهاجمی (Aggressive) - دنبال کردن الگوها"
        }[x]
    )

    st.divider()

    col_reset, col_clear = st.columns(2)
    if col_reset.button("🔄 بازی جدید"):
        st.session_state.revealed = set()
        st.session_state.current_suggestion = None
        st.session_state.mode = 'play'
        st.rerun()

    if col_clear.button("🗑️ پاکسازی تاریخچه"):
        st.session_state.analyzer = MineAnalyzer()
        st.success("تاریخچه پاک شد!")
        st.rerun()

    st.info(f"📊 بازی‌های ثبت شده در حافظه: {len(st.session_state.analyzer.history)}")

# --- Main Interface ---
st.title("💣 تحلیل‌گر پیشرفته ماینز (Mines Analyzer v2)")

# Stats Row
c1, c2, c3 = st.columns(3)
revealed_count = len(st.session_state.revealed)
prob = calculate_next_safe_probability(revealed_count, mines_count)
mult = calculate_multiplier(revealed_count, mines_count)

c1.metric("ضریب (Multiplier)", f"{mult}x")
c2.metric("شانس امن بودن (Safe Probability)", f"{prob:.1f}%")
c3.metric("خانه‌های باز شده", revealed_count)

st.divider()

# --- Analysis & Visualization (Heatmap) ---
# We calculate the heatmap regardless of mode to show the user "Data"
heatmap_data = st.session_state.analyzer.calculate_heatmap()
grid_vals = [[heatmap_data.get(r*5 + c, 0) for c in range(5)] for r in range(5)]

# Create Plotly Heatmap
fig = go.Figure(data=go.Heatmap(
    z=grid_vals,
    x=[f"Col {i+1}" for i in range(5)],
    y=[f"Row {i+1}" for i in range(5)],
    colorscale='RdYlGn_r', # Red to Green (Reversed: Low freq = Green/Safe, High freq = Red/Danger)?
                           # Actually: Heatmap tracks MINE frequency. So High Value = More Mines = Red.
                           # Low Value = Fewer Mines = Green.
                           # RdYlGn (Red-Yellow-Green) -> High is Green. We want High (Mines) to be Red.
                           # So 'RdYlGn_r' (Reversed) -> High=Red, Low=Green. Correct.
    showscale=True,
    text=[[f"{val:.2f}" for val in row] for row in grid_vals],
    texttemplate="%{text}",
    hoverinfo='z'
))
fig.update_layout(
    title="نقشه حرارتی خطر (Risk Heatmap)",
    xaxis_side="top",
    height=400,
    margin=dict(l=20, r=20, t=40, b=20)
)

# Layout: Left for Grid (Interaction), Right for Heatmap (Analysis)
col_grid, col_viz = st.columns([1, 1])

with col_viz:
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟥 قرمز = خطر بالا (محل تکرار بمب) | 🟩 سبز = امن‌تر (کمتر دیده شده)")

    # Suggestion Button
    if st.button("✨ دریافت پیشنهاد هوشمند (AI Suggestion)", type="primary"):
        sugg = st.session_state.analyzer.suggest_tile(
            list(st.session_state.revealed),
            strategy=strategy
        )
        st.session_state.current_suggestion = sugg
        if sugg is None:
            st.warning("همه خانه‌ها باز شده‌اند یا داده‌ای برای تحلیل نیست.")

    if st.session_state.mode == 'play':
        if st.button("📝 ثبت باخت (مکان بمب‌ها را وارد کنید)"):
            st.session_state.mode = 'input_mines'
            st.rerun()

with col_grid:
    st.subheader("صفحه بازی (Game Grid)")

    # Input Mode Handling
    if st.session_state.mode == 'input_mines':
        st.warning("💣 لطفا روی خانه‌هایی که **بمب** بودند کلیک کنید، سپس 'ثبت' را بزنید.")

        # Temporary state for inputting mines
        if 'input_mines_indices' not in st.session_state:
            st.session_state.input_mines_indices = set()

        # Grid for Input
        for r in range(5):
            cols = st.columns(5)
            for c in range(5):
                idx = r*5 + c
                is_selected = idx in st.session_state.input_mines_indices
                label = "💣" if is_selected else " "

                if cols[c].button(label, key=f"input_{idx}"):
                    if idx in st.session_state.input_mines_indices:
                        st.session_state.input_mines_indices.remove(idx)
                    else:
                        st.session_state.input_mines_indices.add(idx)
                    st.rerun()

        if st.button("✅ ثبت نهایی و ذخیره در هوش مصنوعی"):
            st.session_state.analyzer.add_game(list(st.session_state.input_mines_indices))
            st.session_state.input_mines_indices = set() # Reset
            st.session_state.mode = 'play'
            st.session_state.revealed = set() # New game starts
            st.session_state.current_suggestion = None
            st.success("اطلاعات ذخیره شد! تحلیل‌گر هوشمندتر شد.")
            st.rerun()

    else:
        # Play Mode Grid
        for r in range(5):
            cols = st.columns(5)
            for c in range(5):
                idx = r*5 + c

                # Visual State
                is_revealed = idx in st.session_state.revealed
                is_suggested = (idx == st.session_state.current_suggestion)

                label = "❓"
                if is_revealed:
                    label = "💎"
                elif is_suggested:
                    label = "✨"

                # Button Logic
                # If revealed, disable
                if cols[c].button(label, key=f"play_{idx}", disabled=is_revealed, help=f"Tile {idx}"):
                    st.session_state.revealed.add(idx)
                    # If we clicked the suggestion, clear it
                    if is_suggested:
                        st.session_state.current_suggestion = None
                    st.rerun()

import streamlit as st
import plotly.graph_objects as go
from market_data import get_historical_data
from ai_analyst import analyze_market

# Page Configuration
st.set_page_config(page_title="ربات سیگنال هوشمند", page_icon="📈", layout="wide")

# Custom CSS for RTL support and font
st.markdown("""
<style>
    body {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', sans-serif;
    }
    .stMarkdown, .stButton, .stSelectbox, .stTextInput {
        direction: rtl;
        text-align: right;
    }
    /* Align Streamlit's default elements to right */
    .css-10trblm {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 ربات سیگنال‌دهی هوشمند (AI Signal Bot)")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("تنظیمات (Settings)")

    api_key = st.text_input("کلید API گوگل (Google API Key)", type="password", help="کلید API خود را از Google AI Studio دریافت کنید.")

    symbol = st.text_input("نماد (Symbol)", value="BTC-USD", help="مثال: BTC-USD, ETH-USD, AAPL")

    period = st.selectbox("بازه زمانی (Period)", ["1mo", "3mo", "6mo", "1y"], index=1)
    interval = st.selectbox("تایم‌فریم (Timeframe)", ["1d", "1h", "4h"], index=0)

    analyze_btn = st.button("تحلیل و دریافت سیگنال")

# Main Content
if analyze_btn:
    if not api_key:
        st.error("⚠️ لطفاً کلید API گوگل را وارد کنید.")
    elif not symbol:
        st.error("⚠️ لطفاً نماد مورد نظر را وارد کنید.")
    else:
        with st.spinner('در حال دریافت اطلاعات بازار...'):
            data = get_historical_data(symbol, period=period, interval=interval)

        if data is not None:
            # Display Chart
            st.subheader(f"نمودار قیمت: {symbol}")

            fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                            open=data['Open'],
                            high=data['High'],
                            low=data['Low'],
                            close=data['Close'],
                            name=symbol)])

            # Add SMA 50
            fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='orange')))

            fig.update_layout(xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)

            # AI Analysis
            with st.spinner('هوش مصنوعی در حال تحلیل بازار است...'):
                analysis_result = analyze_market(data, api_key, symbol)

            st.subheader("📊 تحلیل هوش مصنوعی")
            st.markdown("---")
            st.markdown(analysis_result)

        else:
            st.error("❌ خطا در دریافت اطلاعات. لطفاً نماد را بررسی کنید.")

else:
    st.info("👈 لطفاً تنظیمات را در منوی سمت چپ وارد کرده و دکمه تحلیل را بزنید.")

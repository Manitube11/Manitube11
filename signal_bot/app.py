import streamlit as st
import plotly.graph_objects as go
from market_data import get_historical_data
from ai_analyst import analyze_market

# Page Configuration
st.set_page_config(page_title="ربات سیگنال حرفه‌ای", page_icon="📈", layout="wide")

# Custom CSS for RTL support and font
st.markdown("""
<style>
    body {
        direction: rtl;
        text-align: right;
        font-family: 'Tahoma', sans-serif;
    }
    .stMarkdown, .stButton, .stSelectbox, .stTextInput, .stTab {
        direction: rtl;
        text-align: right;
    }
    /* Align Streamlit's default elements to right */
    .css-10trblm {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Curated List of Assets
CRYPTO_PAIRS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
    "TRX-USD", "MATIC-USD", "DOT-USD", "LTC-USD", "SHIB-USD", "AVAX-USD", "LINK-USD",
    "ATOM-USD", "XMR-USD", "ETC-USD", "BCH-USD", "XLM-USD", "ALGO-USD", "FIL-USD"
]

FOREX_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X",
    "NZDUSD=X", "GC=F", "SI=F", "CL=F" # Gold, Silver, Crude Oil
]

ALL_ASSETS = ["--- Crypto ---"] + CRYPTO_PAIRS + ["--- Forex/Commodities ---"] + FOREX_PAIRS + ["Custom..."]

# Header
st.title("🤖 ربات سیگنال‌دهی حرفه‌ای (Pro AI Trader)")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ تنظیمات (Settings)")

    api_key = st.text_input("🔑 کلید API گوگل (Gemini API Key)", type="password", help="کلید API خود را وارد کنید.")

    asset_choice = st.selectbox("💎 انتخاب دارایی (Asset)", ALL_ASSETS, index=1)

    symbol = asset_choice
    if asset_choice == "Custom...":
        symbol = st.text_input("✍️ نماد دلخواه (مثال: TSLA)", value="BTC-USD")
    elif "---" in asset_choice:
        st.error("لطفا یک دارایی معتبر انتخاب کنید.")
        symbol = ""

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("بازه (Period)", ["1mo", "3mo", "6mo", "1y"], index=1)
    with col2:
        interval = st.selectbox("تایم‌فریم", ["1d", "1h", "4h", "1wk"], index=0)

    analyze_btn = st.button("🚀 تحلیل و سیگنال")

# Main Content
if analyze_btn:
    if not api_key:
        st.error("⚠️ لطفاً کلید API گوگل را وارد کنید.")
    elif not symbol:
        st.error("⚠️ لطفاً نماد مورد نظر را وارد کنید.")
    else:
        with st.spinner('🔄 در حال دریافت اطلاعات بازار و محاسبه اندیکاتورها...'):
            data = get_historical_data(symbol, period=period, interval=interval)

        if data is not None:
            # Create Tabs
            tab1, tab2, tab3 = st.tabs(["📉 نمودار قیمت (Chart)", "📊 اندیکاتورها (Indicators)", "🤖 هوش مصنوعی (AI Signal)"])

            with tab1:
                st.subheader(f"نمودار تکنیکال: {symbol}")
                fig = go.Figure()

                # Candlestick
                fig.add_trace(go.Candlestick(x=data['Date'],
                                open=data['Open'], high=data['High'],
                                low=data['Low'], close=data['Close'],
                                name='Price'))

                # EMA 50
                fig.add_trace(go.Scatter(x=data['Date'], y=data['EMA_50'], mode='lines', name='EMA 50', line=dict(color='orange')))

                # Bollinger Bands
                fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dot')))
                fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dot'), fill='tonexty'))

                fig.update_layout(xaxis_rangeslider_visible=False, height=600, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("وضعیت اندیکاتورها")

                # MACD Chart
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=data['Date'], y=data['MACD_Line'], mode='lines', name='MACD Line', line=dict(color='blue')))
                fig_macd.add_trace(go.Scatter(x=data['Date'], y=data['MACD_Signal'], mode='lines', name='Signal Line', line=dict(color='orange')))
                fig_macd.add_trace(go.Bar(x=data['Date'], y=data['MACD_Hist'], name='Histogram'))
                fig_macd.update_layout(height=300, title="MACD", template="plotly_dark")
                st.plotly_chart(fig_macd, use_container_width=True)

                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=data['Date'], y=data['RSI_14'], mode='lines', name='RSI', line=dict(color='purple')))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                fig_rsi.update_layout(height=300, title="RSI (14)", yaxis=dict(range=[0, 100]), template="plotly_dark")
                st.plotly_chart(fig_rsi, use_container_width=True)

            with tab3:
                # AI Analysis
                with st.spinner('🧠 هوش مصنوعی در حال تحلیل بازار است (لطفاً صبر کنید)...'):
                    analysis_result = analyze_market(data, api_key, symbol)

                st.subheader("📋 سیگنال و تحلیل هوش مصنوعی")
                st.success("تحلیل با موفقیت انجام شد!")
                st.markdown("---")
                st.markdown(analysis_result)

        else:
            st.error(f"❌ خطا در دریافت اطلاعات برای نماد {symbol}. لطفاً نماد را بررسی کنید.")

else:
    st.info("👈 لطفاً تنظیمات را در منوی سمت چپ وارد کرده و دکمه تحلیل را بزنید.")

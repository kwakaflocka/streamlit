import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

st.set_page_config(page_title="Crypto & Stock Market Analyzer", layout="wide")
st.title("📈 Crypto & Stock Market Analyzer")

# Sidebar inputs
asset1 = st.sidebar.text_input("Enter First Ticker (e.g. BTC-USD, AAPL)", value="BTC-USD")
asset2 = st.sidebar.text_input("Enter Second Ticker (optional)", value="ETH-USD")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Fetch data
def load_data(ticker):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        data = data[["Close"]].rename(columns={"Close": ticker})
        return data
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")
        return pd.DataFrame()

data1 = load_data(asset1)
data2 = load_data(asset2) if asset2 else None

# Merge data for correlation
if not data1.empty and data2 is not None and not data2.empty:
    combined = data1.join(data2, how="inner")
    corr, p_value = pearsonr(combined[asset1], combined[asset2])

    st.subheader("🔗 Correlation Analysis")
    st.write(f"Correlation between **{asset1}** and **{asset2}**: `r = {corr:.2f}` (p = {p_value:.3f})")

    st.line_chart(combined)

# Plot individual asset performance
col1, col2 = st.columns(2)

with col1:
    if not data1.empty:
        st.subheader(f"📊 {asset1} Closing Prices")
        st.line_chart(data1)

with col2:
    if data2 is not None and not data2.empty:
        st.subheader(f"📊 {asset2} Closing Prices")
        st.line_chart(data2)

# Moving average overlay
if not data1.empty:
    st.subheader(f"📉 {asset1} Trend with Moving Averages")
    ma_window = st.slider("Select Moving Average Window (days)", 5, 100, 20)
    data1[f"MA{ma_window}"] = data1[asset1].rolling(window=ma_window).mean()
    st.line_chart(data1[[asset1, f"MA{ma_window}"]])

# Price change summary
if not data1.empty:
    st.subheader(f"📈 {asset1} Performance Summary")
    returns = data1[asset1].pct_change().dropna()
    st.metric(label="Total Return", value=f"{((data1[asset1].iloc[-1]/data1[asset1].iloc[0]-1)*100):.2f}%")
    st.metric(label="Volatility (Std Dev)", value=f"{returns.std()*100:.2f}%")

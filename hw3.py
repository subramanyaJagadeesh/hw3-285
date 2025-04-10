import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz
import requests
import time

if 'BROWSER' not in st.session_state:
    st.session_state.BROWSER = True
    st._config.set_option('server.runOnSave', True)

st.set_page_config(page_title="📊 Stock Info Fetcher", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    .stTextInput > div > div > input {
        background-color: #333;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📊 Stock Info Fetcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Check real-time stock details by entering a ticker symbol (e.g., AAPL, GOOGL, MSFT).</p>", unsafe_allow_html=True)

symbol = st.text_input("Please enter a stock symbol:", "").upper().strip()

if symbol:
    connection_ok = False
    info = None
    fetch_error_message = None

    try:
        connection_check_start = time.time()
        try:
            requests.get("https://finance.yahoo.com", timeout=5)
            connection_time = time.time() - connection_check_start
            connection_ok = True 

            if connection_time > 2:
                st.warning("⚠️ Your internet connection seems slow. Data retrieval may take longer than usual.")
        except requests.exceptions.RequestException:
            fetch_error_message = "❌ Unable to connect to Yahoo Finance. Please check your internet connection and try again."

        if connection_ok:
            stock = yf.Ticker(symbol)

            try:
                fetched_info = stock.info
                if fetched_info and 'longName' in fetched_info and 'regularMarketPrice' in fetched_info:
                    info = fetched_info 
                elif not fetched_info: 
                     fetch_error_message = f"⚠️ Error: No data returned for '{symbol}'. It might be an invalid symbol."
                else: 
                     fetch_error_message = f"⚠️ Error: Incomplete data received for '{symbol}' (missing name or price)."

            except Exception as e:
                if "failed to establish a new connection" in str(e).lower() or "timed out" in str(e).lower():
                    fetch_error_message = "❌ Connection timeout during data retrieval. Your internet may be slow/unstable."
                else:
                    fetch_error_message = f"⚠️ An error occurred while fetching data for '{symbol}'. Please try again."
                info = None

        if info: 
            tz = pytz.timezone('US/Pacific')
            current_time = datetime.now(tz).strftime("%a %b %d %H:%M:%S %Z %Y")

            name = info.get("longName", "N/A")
            price = info.get("regularMarketPrice", 0.0)
            change = info.get("regularMarketChange", 0.0)
            percent_change = info.get("regularMarketChangePercent", 0.0)

            sign = "+" if change >= 0 else "-"
            formatted_change = f"{sign}{abs(change):.2f}"
            formatted_percent = f"{sign}{abs(percent_change):.2f}%"
            color = "green" if change >= 0 else "red"

            st.markdown(f"### 🕒 {current_time}")
            st.markdown(f"### 🏢 {name} ({symbol})")
            st.markdown(f"<h2 style='color:{color};'>${price:.2f} {formatted_change} ({formatted_percent})</h2>", unsafe_allow_html=True)

        elif fetch_error_message: 
             st.error(fetch_error_message) 

    except Exception as e:
         if not fetch_error_message or ("connection" not in fetch_error_message.lower() and "connect" not in fetch_error_message.lower()):
             st.error(f"⚠️ An unexpected system error occurred: {str(e)}")

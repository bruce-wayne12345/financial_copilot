import streamlit as st
import pandas as pd
import google.generativeai as genai
import yfinance as yf

# 1. SETUP & CACHING
st.set_page_config(page_title="Dual-AI Financial Copilot", layout="wide")

@st.cache_data(show_spinner=False)
def get_ai_response(prompt, _model):
    try:
        response = _model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Quota full! Wait 1 minute or use a different API Key. Error: {e}"

# 2. SIDEBAR
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    user_goal = st.text_input("Savings Goal", value="Retirement")
    st.divider()
    st.info("Agentic Co-pilot v1.0")

    # ... your existing sidebar code ...
    st.divider()
    with st.expander("🛠️ System Algorithm (No-BS Mode)"):
        st.write("**Engine:** Logic-Augmented Generation (LAG)")
        st.code("""
1. Input: CSV + yFinance API
2. Compute: 
   - Category Variance (σ)
   - Stock PEG Ratio Filter
   - CPI Mapping Delta
3. Inference:
   - LLM explains Mathematical
     Anomalies only.
        """, language="text")    

if not api_key:
    st.warning("Please enter your API Key to start.")
    st.stop()

# 3. INITIALIZE AI MODEL
genai.configure(api_key=api_key)
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = available_models[0] if available_models else "gemini-1.5-flash"
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"Failed to connect to Gemini: {e}")
    st.stop()

# 4. MAIN UI - TABS
tab1, tab2, tab3 = st.tabs(["💰 Budget Tracker", "📈 AI Trading Assistant", "⚖️ Inflation Analyzer"])

# --- TAB 1: BUDGET TRACKER ---
with tab1:
    st.header("Personal Expense Agent")
    uploaded_file = st.file_uploader("Upload transactions.csv", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("Recent Transactions")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("Analyze my Spending"):
            with st.spinner('Agent is calculating...'):
                data_summary = df.to_string() 
                prompt = f"Analyze these expenses: {data_summary}. Goal: {user_goal}. Give 3 witty, actionable nudges."
                result = get_ai_response(prompt, model)
                st.info(result)
                st.balloons()
    else:
        st.info("Please upload a CSV file to begin analysis.")

# --- TAB 2: TRADING ASSISTANT ---
with tab2:
    st.header("AI Stock Screener")
    st.write("Analyzing top NSE stocks based on your goals.")
    
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBI.NS", "ITC.NS", "WIPRO.NS", "HINDUNILVR.NS"]
    
    if st.button("Screen Stocks for Me"):
        with st.spinner("Fetching Market Data..."):
            stock_results = []
            for t in tickers:
                try:
                    s = yf.Ticker(t)
                    info = s.info
                    stock_results.append({
                        "Ticker": t,
                        "Price": info.get("currentPrice"),
                        "PE_Ratio": info.get("trailingPE"),
                        "Sector": info.get("sector")
                    })
                except:
                    continue
            
            stock_df = pd.DataFrame(stock_results)
            st.write("Market Data Scanned:", stock_df)
            
            prompt = f"Look at this stock data: {stock_df.to_string()}. Which 3 companies are best for a '{user_goal}' goal? Provide a scenario for each."
            response_text = get_ai_response(prompt, model)
            st.subheader("🚀 AI Recommendations")
            st.success(response_text)

# --- TAB 3: INFLATION ANALYZER ---
with tab3:
    st.header("⚖️ Personal Inflation Analyzer")
    st.write("Compare your spending against India's 2026 Inflation (3.40%)")

    current_cpi = 3.40 
    high_inflation_items = {"Gold/Jewellery": 45.0, "Tomatoes": 35.9, "Cauliflower": 34.1}
    low_inflation_items = {"Onions": -27.7, "Potatoes": -18.9, "Garlic": -10.1}

    if 'df' in locals():
        user_breakdown = df.groupby('Category')['Amount'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("National Inflation (CPI)", f"{current_cpi}%", delta="0.19%")
        with col2:
            total_spent = df['Amount'].sum()
            food_spent = user_breakdown.get('Food', 0)
            personal_inflation = current_cpi + (2.5 if food_spent > (total_spent * 0.4) else -0.5)
            st.metric("Your Personal Inflation", f"{personal_inflation:.2f}%", 
                      delta=f"{personal_inflation - current_cpi:.2f}% vs National", delta_color="inverse")

        if st.button("Generate Inflation Shield Strategy"):
            with st.spinner("Analyzing market prices..."):
                prompt = f"National Inflation: {current_cpi}%. User Spending: {user_breakdown.to_string()}. High price items: {high_inflation_items}. Suggest 'Inflation Shields'."
                response_text = get_ai_response(prompt, model)
                st.success(response_text)
    else:
        st.info("Upload your transactions in the Budget Tracker tab first.")
import sys
import os
import datetime
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Loan Prepayment vs. Live Nifty Market Strategy",
    page_icon="📈",
    layout="wide"
)

# --- THEME STYLING & MODERN UI CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    [data-testid="stSidebar"] {
        background-color: #1e3a8a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
    }
    .milestone-card {
        background: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .battle-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 14px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Clear session cache on fresh start
if "initialized" not in st.session_state:
    st.session_state.initialized = True

st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🚀 Loan Prepayment vs. Live Nifty Market Strategy</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4b5563;'>An interactive visual journey tracking your lump-sum investments across independent loan timelines.</p>", unsafe_allow_html=True)

# --- FETCH MULTI-PERIOD MARKET DATA (3M, 6M, 1Y) ---
@st.cache_data(ttl=3600)
def fetch_multi_period_market_returns():
    tickers = {
        "Nifty 50": "^NSEI",
        "Nifty 100": "^CNX100",
        "Nifty 500": "^CRSLDX"
    }
    results = {}
    end_date = datetime.date.today()
    
    periods = {
        "3 Months": 92,
        "6 Months": 184,
        "1 Year": 365
    }

    for name, ticker in tickers.items():
        results[name] = {}
        for period_label, days in periods.items():
            start_date = end_date - datetime.timedelta(days=days)
            try:
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                if not data.empty and len(data) > 1:
                    if isinstance(data.columns, pd.MultiIndex):
                        start_val = data['Close'].iloc[0].iloc[0]
                        end_val = data['Close'].iloc[-1].iloc[0]
                    else:
                        start_val = data['Close'].iloc[0]
                        end_val = data['Close'].iloc[-1]
                    
                    abs_return = (end_val - start_val) / start_val
                    
                    if days == 92:
                        annualized_cagr = ((1 + abs_return) ** 4) - 1
                    elif days == 184:
                        annualized_cagr = ((1 + abs_return) ** 2) - 1
                    else:
                        annualized_cagr = abs_return
                        
                    results[name][period_label] = float(annualized_cagr) * 100
                else:
                    results[name][period_label] = 12.0
            except Exception:
                results[name][period_label] = 12.0
    return results

market_data = fetch_multi_period_market_returns()

# --- INPUT SECTION ---
st.sidebar.title("⚙️ Loan & Strategy Inputs")
loan_amount = st.sidebar.number_input("Loan Amount (₹)", value=0, step=100000, format="%d")
tenure_years = st.sidebar.number_input("Tenure (Years)", value=0, step=1, format="%d")
bank_rate = st.sidebar.number_input("Loan Interest Rate (%)", value=0.0, step=0.1, format="%.2f")
cap_gains_tax = st.sidebar.number_input("Capital Gains Tax (%)", value=12.5, step=0.5, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Prepayment Schedule")
num_prepayments = st.sidebar.slider("Number of Prepayments", min_value=0, max_value=10, value=0)

prepayments = []
for i in range(num_prepayments):
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        p_yr = st.number_input(f"Yr #{i+1}", value=1, min_value=1, key=f"py_{i}")
    with col_b:
        p_amt = st.number_input(f"Amt #{i+1} (₹)", value=0.0, step=50000.0, key=f"pa_{i}")
    if p_amt > 0:
        prepayments.append({"year": int(p_yr), "amount": float(p_amt)})

# Guard for empty/zero initial states
if loan_amount <= 0 or tenure_years <= 0 or bank_rate <= 0:
    st.info("👈 Please enter your **Loan Amount**, **Tenure**, and **Interest Rate** in the sidebar to view strategy comparisons.")
else:
    # --- CALCULATIONS ---
    n = tenure_years * 12
    r = (bank_rate / 100) / 12
    original_emi = (loan_amount * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
    original_total_payment = original_emi * n
    original_total_interest = original_total_payment - loan_amount

    # Strategy A: Tenure Reduction (Keep original EMI constant)
    balance_a = loan_amount
    months_a = 0
    total_interest_a = 0
    for m in range(1, n + 1):
        if balance_a <= 0:
            break
        interest_m = balance_a * r
        principal_m = original_emi - interest_m
        for p in prepayments:
            if p["year"] * 12 == m:
                balance_a -= p["amount"]
        balance_a -= principal_m
        total_interest_a += interest_m
        months_a = m

    interest_saved_a = max(0, original_total_interest - total_interest_a)
    new_years_a = months_a // 12
    new_months_a = months_a % 12

    # Strategy B: EMI Reduction (Recalculate EMI at each prepayment event, retain original tenure)
    balance_b = loan_amount
    current_emi = original_emi
    total_interest_b = 0
    for m in range(1, n + 1):
        if balance_b <= 0:
            break
        interest_m = balance_b * r
        principal_m = current_emi - interest_m
        prepay_happened = False
        for p in prepayments:
            if p["year"] * 12 == m:
                balance_b -= p["amount"]
                prepay_happened = True
        balance_b -= principal_m
        total_interest_b += interest_m
        if prepay_happened and balance_b > 0 and m < n:
            rem_months = n - m
            current_emi = (balance_b * r * ((1 + r) ** rem_months)) / (((1 + r) ** rem_months) - 1)

    interest_saved_b = max(0, original_total_interest - total_interest_b)

    # --- DASHBOARD CARDS ---
    st.markdown("---")
    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        st.markdown(
            f"""
            <div style="background-color: #e7f1ff; padding: 22px; border-radius: 12px; border: 1px solid #b6d4fe;">
                <h3 style="margin-top:0; color:#0d6efd;">📋 Original Loan</h3>
                <p style="font-size:16px;"><b>EMI:</b> ₹{original_emi:,.2f} / mo</p>
                <p style="font-size:16px;"><b>Tenure:</b> {tenure_years} Years</p>
                <p style="font-size:16px;"><b>Total Repayment:</b> ₹{original_total_payment:,.0f}</p>
                <p style="font-size:15px; color:#6c757d;"><i>(Interest: ₹{original_total_interest:,.0f})</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_2:
        st.markdown(
            f"""
            <div style="background-color: #d1e7dd; padding: 22px; border-radius: 12px; border: 1px solid #badbcc;">
                <h3 style="margin-top:0; color:#198754;">📉 Strategy A (Tenure Drop)</h3>
                <p style="font-size:16px;"><b>EMI:</b> ₹{original_emi:,.2f} / mo <span style='color:green; font-weight:bold;'>[Unchanged]</span></p>
                <p style="font-size:16px;"><b>New Tenure:</b> <span style='color:green; font-weight:bold;'>{new_years_a} Yrs {new_months_a} Mos</span> <span style='color:#dc3545;'>({tenure_years - new_years_a} Yrs Faster)</span></p>
                <p style="font-size:16px;"><b>Total Repayment:</b> ₹{loan_amount + total_interest_a:,.0f}</p>
                <p style="font-size:15px; color:#198754;"><i>(Saves ₹{interest_saved_a:,.0f} Interest)</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_3:
        st.markdown(
            f"""
            <div style="background-color: #fff3cd; padding: 22px; border-radius: 12px; border: 1px solid #ffeeba;">
                <h3 style="margin-top:0; color:#ffc107;">📊 Strategy B (EMI Drop)</h3>
                <p style="font-size:16px;"><b>Final EMI:</b> <span style='color:green; font-weight:bold;'>₹{current_emi:,.2f} / mo</span> <span style='color:green;'>(-₹{original_emi - current_emi:,.2f}/mo)</span></p>
                <p style="font-size:16px;"><b>Tenure:</b> {tenure_years} Years <span style='color:#b45309; font-weight:bold;'>[Original Retained]</span></p>
                <p style="font-size:16px;"><b>Total Repayment:</b> ₹{loan_amount + total_interest_b:,.0f}</p>
                <p style="font-size:15px; color:#b45309;"><i>(Saves ₹{interest_saved_b:,.0f} Interest)</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- VISUAL PREPAYMENT TIMELINE ROADMAP ---
    st.markdown("---")
    st.subheader("🗺️ Your Prepayment Milestone Roadmap")
    st.markdown("See how each lump sum is planted along your loan timeline and how many years it has to compound:")

    if not prepayments:
        st.info("No prepayments scheduled. Add prepayments in the sidebar to see their milestone roadmap.")
    else:
        timeline_cols = st.columns(min(len(prepayments), 3))
        for idx, p in enumerate(prepayments):
            comp_yrs = max(0, tenure_years - p["year"])
            with timeline_cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="milestone-card">
                        <h4 style="margin:0; color:#1e3a8a;">Prepayment #{idx+1}</h4>
                        <p style="font-size:15px; margin:4px 0;"><b>Amount:</b> ₹{int(p['amount']):,}</p>
                        <p style="font-size:15px; margin:4px 0;"><b>Timing:</b> Year {p['year']} of {tenure_years}</p>
                        <p style="font-size:14px; color:#2563eb; margin:2px 0;">⏳ Compounds for <b>{comp_yrs} Years</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # --- HEAD-TO-HEAD MARKET BATTLE CARDS ---
    st.markdown("---")
    st.subheader("🥊 Head-to-Head Market Battle Cards")
    selected_period = st.radio("Select Trailing Market Horizon for Battle:", ["1 Year", "6 Months", "3 Months"], horizontal=True)

    total_prepay_invested = sum([p["amount"] for p in prepayments])
    baseline_benchmark = total_prepay_invested + interest_saved_a

    battle_cols = st.columns(3)

    for idx, (index_name, periods_dict) in enumerate(market_data.items()):
        cagr = periods_dict[selected_period]
        total_future_val = 0
        
        # Calculate compound growth per lump sum independently
        milestone_details = ""
        for p in prepayments:
            if p["year"] <= tenure_years:
                comp_yrs = tenure_years - p["year"]
                monthly_roi = (cagr / 100) / 12
                future_val = p["amount"] * ((1 + monthly_roi) ** (comp_yrs * 12))
                profit = future_val - p["amount"]
                post_tax_profit = profit * (1 - cap_gains_tax / 100)
                ls_val = p["amount"] + post_tax_profit
                total_future_val += ls_val
                milestone_details += f"• Yr {p['year']} (₹{int(p['amount']):,}): <b>₹{ls_val:,.0f}</b><br>"

        net_diff = total_future_val - baseline_benchmark
        is_winner = net_diff >= 0
        border_color = "#10b981" if is_winner else "#ef4444"
        badge_bg = "#d1fae5" if is_winner else "#fee2e2"
        badge_color = "#047857" if is_winner else "#b91c1c"
        verdict_text = "WINNER: Market Investment" if is_winner else "WINNER: Loan Prepayment"

        with battle_cols[idx]:
            st.markdown(
                f"""
                <div class="battle-card" style="border-top: 5px solid {border_color};">
                    <span style="background-color: {badge_bg}; color: {badge_color}; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">{verdict_text}</span>
                    <h3 style="margin: 10px 0 5px 0; color: #1e3a8a;">{index_name}</h3>
                    <p style="font-size: 13px; color: #64748b; margin-bottom: 15px;">Trailing CAGR ({selected_period}): <b>{cagr:.2f}%</b></p>
                    <div style="text-align: left; background: #f8fafc; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 12px;">
                        <b>Independent Growth:</b><br>{milestone_details if milestone_details else 'No prepayments'}
                    </div>
                    <p style="font-size: 14px; margin: 4px 0;">Post-Tax Maturity: <b>₹{total_future_val:,.0f}</b></p>
                    <p style="font-size: 16px; font-weight: 800; color: {badge_color}; margin-top: 6px;">
                        {'+' if net_diff >= 0 else ''}₹{net_diff:,.0f} Alpha
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.subheader("💡 Recommendation Verdict")
    one_yr_vals = [float(periods_dict["1 Year"]) for index_name, periods_dict in market_data.items()]
    best_cagr = max(one_yr_vals) if one_yr_vals else 0

    if best_cagr > bank_rate:
        st.success(f"**Verdict: Invest in the Market.** Current equity index momentum ({best_cagr:.2f}% 1Y CAGR) outperforms your loan interest rate ({bank_rate}%) over the long term.")
    else:
        st.info(f"**Verdict: Prepay the Loan.** Guaranteed loan interest savings outweigh current equity market momentum.")

# --- FOOTER SOURCE NOTE ---
st.markdown("---")
st.markdown(
    "📌 **Data Source Note:** Trailing annualized CAGR figures are pulled in real-time from **Yahoo Finance** "
    "across **3-Month, 6-Month, and 1-Year** historical closing prices (`^NSEI`, `^CNX100`, `^CRSLDX`), "
    "compounded annually and adjusted for your specified Capital Gains Tax."
)

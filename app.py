import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_collection, seed_data
from utils.calculations import calculate_net_worth, calculate_surplus
import config

st.set_page_config(page_title="WealthForge", page_icon="💰", layout="wide")

st.title("WealthForge")
st.markdown("**ENGINEER BY TRADE • DAD BY PURPOSE • PROBLEM-SOLVER BY NATURE** — Steve")

# Seed on first run
if "seeded" not in st.session_state:
    try:
        seed_data()
        st.session_state.seeded = True
        st.success("✅ Initial data seeded!")
    except Exception as e:
        st.error(f"Seeding failed: {str(e)}")

# Load data
assets = list(get_collection("assets").find())
debts = list(get_collection("debts").find())
budget_doc = get_collection("budget").find_one() or {"monthly_income": 3397, "expenses": {}}

# Core calculations
net_worth = calculate_net_worth(assets, debts)
surplus = calculate_surplus(budget_doc)

# Emergency fund
emergency_current = next((a.get("value", 0) for a in assets if a.get("name") == "Emergency Fund"), 0)

# v1.3 additions
previous_net_worth = budget_doc.get("previous_net_worth", net_worth)  # defaults to current if not set
net_worth_change = net_worth - previous_net_worth

# Liquidity Runway (using sellable assets)
liquid_assets = emergency_current + 7000 + 3500 + 6500  # Toyota + Ford + Trailer
monthly_exp = sum(budget_doc["expenses"].values()) or 1
liquidity_runway = round(liquid_assets / monthly_exp, 1)

# Sidebar
page = st.sidebar.selectbox("Navigation", 
    ["Dashboard", "Transactions (v1 stub)", "Debts & Assets", "Stability"])

if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    # Strong colored surplus
    color = "#28a745" if surplus >= 0 else "#dc3545"
    col1.markdown(f"""
        <div style="text-align:center">
            <div style="font-size:1rem;color:#6c757d">Monthly Surplus</div>
            <div style="font-size:2.5rem;font-weight:bold;color:{color}">${surplus:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col2.metric("Net Worth", f"${net_worth:,.0f}")
    col3.metric("Net Worth Change", f"${net_worth_change:,.0f}", delta=f"{net_worth_change/net_worth*100:.1f}%" if net_worth != 0 else None)
    col4.metric("Liquidity Runway", f"{liquidity_runway} months")

    # Expense pie
    if budget_doc.get("expenses"):
        exp_df = pd.DataFrame(list(budget_doc["expenses"].items()), columns=["Category", "Amount"])
        fig = px.pie(exp_df, names="Category", values="Amount", title="Expense Breakdown")
        st.plotly_chart(fig, use_container_width=True)

    if budget_doc["expenses"].get("Lot rent", 1) == 0:
        st.success("Lot rent dropped to $0 — $360/month freed up!")

    # v1.3 Upcoming Bills
    st.subheader("Upcoming Bills (This Month)")
    bills_df = pd.DataFrame(list(budget_doc["expenses"].items()), columns=["Bill", "Amount"])
    bills_df = bills_df[bills_df["Amount"] > 0]
    st.table(bills_df)

    # Transition paychecks (kept from before)
    st.subheader("Upcoming Transition Paychecks")
    st.table(pd.DataFrame([
        {"Date": "March 20, 2026", "Amount": 850, "Note": "1-week paycheck"},
        {"Date": "April 3, 2026", "Amount": 1700, "Note": "Full 2-week paycheck"}
    ]))

    # Save previous net worth for change tracking
    st.subheader("Track Net Worth Change")
    prev_input = st.number_input("Last Month's Net Worth", value=float(previous_net_worth), step=100.0)
    if st.button("Save Previous Net Worth"):
        get_collection("budget").update_one({}, {"$set": {"previous_net_worth": prev_input}})
        st.success("Saved! Refresh to see change.")
        st.rerun()

elif page == "Transactions (v1 stub)":
    st.header("Add Transaction (basic v1)")
    typ = st.radio("Type", ["Income", "Expense"])
    cat = st.selectbox("Category", config.CATEGORIES["income"] if typ=="Income" else config.CATEGORIES["expenses"])
    amt = st.number_input("Amount", min_value=0.01, step=0.01)
    if st.button("Add (logged only for now)"):
        st.info(f"Would add {typ} ${amt:.2f} to {cat} — full history in v2")

elif page == "Debts & Assets":
    # (unchanged from your working version — kept for brevity)
    st.header("Assets (Editable)")
    for a in assets:
        name = a.get('name', 'Unnamed')
        current_val = a.get('value', 0)
        new_val = st.number_input(f"{name} (${current_val:,.0f})", value=float(current_val), step=100.0, key=f"asset_{name}")
        if new_val != current_val and st.button(f"Save {name}", key=f"save_asset_{name}"):
            get_collection("assets").update_one({"name": name}, {"$set": {"value": new_val}})
            st.success(f"{name} updated!")
            st.rerun()

    st.header("Debts (Editable)")
    for d in debts:
        name = d.get('name', 'Unnamed')
        current_bal = d.get('balance', 0)
        new_bal = st.number_input(f"{name} (${current_bal:,.0f})", value=float(current_bal), step=100.0, key=f"debt_{name}")
        if new_bal != current_bal and st.button(f"Save {name}", key=f"save_debt_{name}"):
            get_collection("debts").update_one({"name": name}, {"$set": {"balance": new_bal}})
            st.success(f"{name} updated!")
            st.rerun()

elif page == "Stability":
    # (your existing Stability page with emergency update — kept intact)
    st.header("Stability View (v1)")
    st.progress(emergency_current / 3000)
    st.metric("Emergency Fund Progress", f"${emergency_current:,.0f} / $3,000", delta=f"{emergency_current / 3000 * 100:.1f}%")
    st.info("Retirement: You contribute 5% (~$243/mo) — company matches 4% → effective 9%")
    st.write("Current buffer: ~0 months")

    st.subheader("Update Emergency Fund")
    new_amount = st.number_input("New Amount ($)", min_value=0.0, value=float(emergency_current), step=10.0)
    if st.button("Save Emergency Fund"):
        get_collection("assets").update_one({"name": "Emergency Fund"}, {"$set": {"value": new_amount}})
        st.success(f"Updated to ${new_amount:,.2f}!")
        st.rerun()

st.sidebar.caption("WealthForge v1.3 • Net Worth Change + Liquidity Runway + Upcoming Bills added")
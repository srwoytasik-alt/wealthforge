import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

from db import get_collection, seed_data
from utils.calculations import calculate_net_worth, calculate_surplus
import config

st.set_page_config(page_title="WealthForge", page_icon="💰", layout="wide")

st.title("WealthForge")
st.markdown("**ENGINEER BY TRADE • DAD BY PURPOSE • PROBLEM-SOLVER BY NATURE** — Steve")

# -----------------------------
# Seed database
# -----------------------------

if "seeded" not in st.session_state:
    try:
        seed_data()
        st.session_state.seeded = True
    except:
        pass

# -----------------------------
# Load collections
# -----------------------------

assets = list(get_collection("assets").find())
debts = list(get_collection("debts").find())
budget_doc = get_collection("budget").find_one() or {"monthly_income": 3397, "expenses": {}}

# -----------------------------
# Budget mode selector
# -----------------------------

budget_mode = st.sidebar.selectbox(
    "Budget Profile",
    ["Transition (Now → June)", "Full Budget (Post-June)"]
)

expenses = budget_doc.get("expenses", {}).copy()

if budget_mode == "Transition (Now → June)":
    for item in ["property tax", "holidays/car registration", "retirement 5%"]:
        if item in expenses:
            expenses[item] = 0

budget_doc["expenses"] = expenses

# -----------------------------
# Calculations
# -----------------------------

net_worth = calculate_net_worth(assets, debts)
surplus = calculate_surplus(budget_doc)

# emergency fund
emergency_current = next(
    (a.get("value", 0) for a in assets if a.get("name") == "Emergency Fund"),
    0
)

# -----------------------------
# Net worth history logging
# -----------------------------

history_col = get_collection("networth_history")

today = date.today()

existing = history_col.find_one({"date": today.isoformat()})

if not existing:
    history_col.insert_one({
        "date": today.isoformat(),
        "timestamp": datetime.utcnow(),
        "net_worth": net_worth
    })

# -----------------------------
# Navigation
# -----------------------------

page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Net Worth", "Transactions", "Debts & Assets", "Stability"]
)

# =========================================================
# Dashboard
# =========================================================

if page == "Dashboard":

    col1, col2, col3 = st.columns(3)

    surplus_color = "normal" if surplus >= 0 else "inverse"

    col1.metric(
        "Monthly Surplus",
        f"${surplus:,.0f}",
        delta_color=surplus_color
    )

    col2.metric(
        "Net Worth",
        f"${net_worth:,.0f}"
    )

    col3.metric(
        "Emergency Fund",
        f"${emergency_current:,.0f} / $3,000",
        f"{(emergency_current/3000)*100:.0f}%"
    )

    st.divider()

    if expenses:

        exp_df = pd.DataFrame(
            list(expenses.items()),
            columns=["Category", "Amount"]
        )

        fig = px.pie(
            exp_df,
            names="Category",
            values="Amount",
            title="Expense Breakdown"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Upcoming Paychecks")

    transition_data = [
        {"Date": "March 20 2026", "Amount": 850},
        {"Date": "April 3 2026", "Amount": 1700}
    ]

    st.table(pd.DataFrame(transition_data))


# =========================================================
# Net Worth Page
# =========================================================

elif page == "Net Worth":

    st.header("Net Worth History")

    history = list(history_col.find().sort("timestamp", 1))

    if history:

        hist_df = pd.DataFrame(history)

        hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])

        fig = px.line(
            hist_df,
            x="timestamp",
            y="net_worth",
            title="Net Worth Over Time"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Current Assets")

    for a in assets:
        st.write(f"{a.get('name')}: ${a.get('value',0):,.0f}")

    st.subheader("Current Debts")

    for d in debts:
        st.write(f"{d.get('name')}: ${d.get('balance',0):,.0f}")

    st.metric("Total Net Worth", f"${net_worth:,.0f}")


# =========================================================
# Transactions
# =========================================================

elif page == "Transactions":

    st.header("Transactions (v1 stub)")

    typ = st.radio("Type", ["Income", "Expense"])

    category = st.selectbox(
        "Category",
        config.CATEGORIES["income"] if typ == "Income"
        else config.CATEGORIES["expenses"]
    )

    amount = st.number_input("Amount", min_value=0.01)

    if st.button("Add Transaction"):
        st.info(f"Would log {typ} ${amount:.2f} in {category}")


# =========================================================
# Debts & Assets
# =========================================================

elif page == "Debts & Assets":

    st.header("Assets")

    for a in assets:

        name = a.get("name")
        current_val = a.get("value", 0)

        new_val = st.number_input(
            f"{name}",
            value=float(current_val),
            step=100.0,
            key=f"asset_{name}"
        )

        if new_val != current_val and st.button(
            f"Save {name}", key=f"save_asset_{name}"
        ):
            get_collection("assets").update_one(
                {"name": name},
                {"$set": {"value": new_val}}
            )
            st.success(f"{name} updated!")
            st.rerun()

    st.header("Debts")

    for d in debts:

        name = d.get("name")
        current_bal = d.get("balance", 0)

        new_bal = st.number_input(
            f"{name}",
            value=float(current_bal),
            step=100.0,
            key=f"debt_{name}"
        )

        if new_bal != current_bal and st.button(
            f"Save {name}", key=f"save_debt_{name}"
        ):
            get_collection("debts").update_one(
                {"name": name},
                {"$set": {"balance": new_bal}}
            )
            st.success(f"{name} updated!")
            st.rerun()


# =========================================================
# Stability
# =========================================================

elif page == "Stability":

    st.header("Financial Stability")

    progress_value = min(emergency_current / 3000, 1.0)

    st.progress(progress_value)

    st.metric(
        "Emergency Fund",
        f"${emergency_current:,.0f} / $3,000",
        f"{progress_value*100:.1f}%"
    )

    st.subheader("Update Emergency Fund")

    new_amount = st.number_input(
        "New Amount",
        min_value=0.0,
        value=float(emergency_current),
        step=10.0
    )

    if st.button("Save Emergency Fund"):
        get_collection("assets").update_one(
            {"name": "Emergency Fund"},
            {"$set": {"value": new_amount}}
        )
        st.success("Emergency fund updated")
        st.rerun()

# -----------------------------
# Footer
# -----------------------------

st.sidebar.caption("WealthForge v1 • Streamlit + MongoDB • LifeOS Finance Module")
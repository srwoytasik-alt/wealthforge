import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_collection, seed_data
from utils.calculations import calculate_net_worth, calculate_surplus
import config

st.set_page_config(page_title="WealthForge", page_icon="💰", layout="wide")

st.title("WealthForge")
st.markdown("**ENGINEER BY TRADE • DAD BY PURPOSE • PROBLEM-SOLVER BY NATURE** — Steve")

# Seed on first run (with error handling)
if "seeded" not in st.session_state:
    try:
        seed_data()
        st.session_state.seeded = True
        st.success("✅ Initial data seeded from your June/post-June numbers!")
    except Exception as e:
        st.error(f"Seeding failed: {str(e)}")

# Load data (with fallback if collection empty)
assets = list(get_collection("assets").find())
debts = list(get_collection("debts").find())
budget_doc = get_collection("budget").find_one() or {"monthly_income": 3397, "expenses": {}}

# Calculate core values
net_worth = calculate_net_worth(assets, debts)
surplus = calculate_surplus(budget_doc)

# Find emergency fund value safely
emergency_current = next(
    (a.get("value", 0) for a in assets if a.get("name") == "Emergency Fund"),
    0
)

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", 
    ["Dashboard", "Transactions (v1 stub)", "Debts & Assets", "Stability"])

if page == "Dashboard":
    col1, col2, col3 = st.columns(3)
    
    # Surplus with color (green positive, red negative)
    surplus_color = "normal" if surplus >= 0 else "inverse"
    col1.metric(
        "Monthly Surplus",
        f"${surplus:,.0f}",
        delta_color=surplus_color
    )
    
    col2.metric("Net Worth", f"${net_worth:,.0f}")
    
    col3.metric(
        "Emergency Fund",
        f"${emergency_current:,.0f} / $3,000",
        f"{emergency_current / 3000 * 100:.0f}%"
    )

    # Expense pie chart
    if budget_doc.get("expenses"):
        exp_df = pd.DataFrame(
            list(budget_doc["expenses"].items()),
            columns=["Category", "Amount"]
        )
        fig = px.pie(exp_df, names="Category", values="Amount", title="Expense Breakdown")
        st.plotly_chart(fig, use_container_width=True)
    
    if budget_doc["expenses"].get("Lot rent", 1) == 0:
        st.success("Lot rent dropped to $0 — $360/month freed up!")

    # Upcoming paychecks section
    st.subheader("Upcoming Transition Paychecks (Post-Job Start)")
    transition_data = [
        {"Date": "March 20, 2026", "Amount": 850, "Note": "1-week paycheck (first at GJ)"},
        {"Date": "April 3, 2026", "Amount": 1700, "Note": "Full 2-week paycheck"},
    ]
    st.table(pd.DataFrame(transition_data))
    st.info("These are allocated for family essentials, family payback, CTQ bills — will roll into standard budget from April 17 onward.")

elif page == "Transactions (v1 stub)":
    st.header("Add Transaction (basic v1)")
    typ = st.radio("Type", ["Income", "Expense"])
    cat = st.selectbox("Category", config.CATEGORIES["income"] if typ=="Income" else config.CATEGORIES["expenses"])
    amt = st.number_input("Amount", min_value=0.01, step=0.01)
    if st.button("Add (logged only for now)"):
        st.info(f"Would add {typ} ${amt:.2f} to {cat} — full history coming in v2")

elif page == "Debts & Assets":
    st.header("Assets (Editable)")
    for a in assets:
        name = a.get('name', 'Unnamed')
        current_val = a.get('value', 0)
        note = f"  ({a.get('note', '')})" if a.get("note") else ""
        new_val = st.number_input(
            f"{name}{note} (${current_val:,.0f})",
            value=float(current_val),
            step=100.0,
            key=f"asset_{name.replace(' ', '_')}"
        )
        if new_val != current_val and st.button(f"Save {name}", key=f"save_asset_{name.replace(' ', '_')}"):
            try:
                get_collection("assets").update_one(
                    {"name": name},
                    {"$set": {"value": new_val}}
                )
                st.success(f"{name} updated to ${new_val:,.2f}!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

    st.header("Debts (Editable)")
    for d in debts:
        name = d.get('name', 'Unnamed')
        current_bal = d.get('balance', 0)
        new_bal = st.number_input(
            f"{name} (${current_bal:,.0f})",
            value=float(current_bal),
            step=100.0,
            key=f"debt_{name.replace(' ', '_')}"
        )
        if new_bal != current_bal and st.button(f"Save {name}", key=f"save_debt_{name.replace(' ', '_')}"):
            try:
                get_collection("debts").update_one(
                    {"name": name},
                    {"$set": {"balance": new_bal}}
                )
                st.success(f"{name} updated to ${new_bal:,.2f}!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

elif page == "Stability":
    st.header("Stability View (v1)")
    
    if emergency_current > 0:
        st.progress(emergency_current / 3000)
    else:
        st.progress(0.0)
    
    st.metric(
        "Emergency Fund Progress",
        f"${emergency_current:,.0f} / $3,000",
        delta=f"{emergency_current / 3000 * 100:.1f}%"
    )
    
    st.info("Retirement: You contribute 5% (~$243/mo) — company matches 4% → effective 9%")
    st.write("Current buffer: ~0 months (building emergency fund first)")

    # Update Emergency Fund
    st.subheader("Update Emergency Fund")
    new_amount = st.number_input(
        "New Amount ($)",
        min_value=0.0,
        value=float(emergency_current),
        step=10.0,
        key="emergency_input"
    )
    if st.button("Save Emergency Fund"):
        try:
            get_collection("assets").update_one(
                {"name": "Emergency Fund"},
                {"$set": {"value": new_amount}}
            )
            st.success(f"Updated to ${new_amount:,.2f}! Refreshing...")
            st.rerun()
        except Exception as e:
            st.error(f"Update failed: {str(e)}")

# Footer
st.sidebar.caption("WealthForge v1 • Local • MongoDB Atlas connected • Updated 2026-03-14")
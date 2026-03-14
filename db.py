import os
from dotenv import load_dotenv
from pymongo import MongoClient
import streamlit as st

load_dotenv()
uri = os.getenv("MONGO_URI")

if not uri:
    st.error("MONGO_URI not found in .env file")
    st.stop()

# try:
#     client = MongoClient(uri)
#     db = client["wealthforge"]
#     # Test connection
#     db.command("ping")
# except Exception as e:
#     st.error(f"Connection failed: {str(e)}")
#     st.stop()

import certifi  # <-- Add this import at the top of db.py (after other imports)

try:
    client = MongoClient(uri, tlsCAFile=certifi.where())  # <-- Key change here
    db = client["wealthforge"]
    # Test connection
    db.command("ping")
    print("MongoDB connection test successful!")  # Optional: visible in terminal
except Exception as e:
    st.error(f"Connection failed: {str(e)}")
    st.stop()

def get_collection(name):
    return db[name]

def seed_data():
    if get_collection("assets").count_documents({}) == 0:
        get_collection("assets").insert_many([
            {"name": "Home", "value": 268000},
            {"name": "Toyota", "value": 7000},
            {"name": "Ford", "value": 3500},
            {"name": "Trailer (selling soon)", "value": 6500, "note": "flip profit projected ~$6.5k"},
            {"name": "Emergency Fund", "value": 0, "goal": 3000}
        ])
        
        get_collection("debts").insert_many([
            {"name": "Student Loan", "balance": 12000},
            {"name": "Credit Cards", "balance": 40000},
            {"name": "Car Loan", "balance": 5206},
            {"name": "Home Loan", "balance": 168000}
        ])
        
        get_collection("budget").insert_one({
            "monthly_income": 3397,
            "expenses": {
                "mortgage": 904,
                "property tax": 334,
                "gas": 160,
                "home Insurance": 130,
                "food": 650,
                "car loan": 340,
                "credit cards": 500,
                "meds": 50,
                "oil changes": 30,
                "holidays/car registration": 242,
                "ChatGPT": 8,
                "Lot rent": 0,
                "retirement 5%": 243
            }
        })
        st.success("✅ Initial data seeded from your June/post-June numbers!")
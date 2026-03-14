import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load local .env file (works locally, ignored on Render)
load_dotenv()

# Read MongoDB URI from environment
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Use the WealthForge database
db = client["wealthforge"]


def get_collection(name):
    """Return a MongoDB collection."""
    return db[name]


def seed_data():
    """Seed initial data if database is empty."""
    assets_col = db["assets"]
    debts_col = db["debts"]
    budget_col = db["budget"]

    if assets_col.count_documents({}) == 0:
        assets_col.insert_many([
            {"name": "Emergency Fund", "value": 0},
            {"name": "Home Value", "value": 268000},
            {"name": "Toyota Corolla", "value": 7000},
            {"name": "Ford Truck", "value": 3500},
            {"name": "Trailer", "value": 6500}
        ])

    if debts_col.count_documents({}) == 0:
        debts_col.insert_many([
            {"name": "Mortgage", "balance": 168000},
            {"name": "Credit Cards", "balance": 40000},
            {"name": "Student Loan", "balance": 12000},
            {"name": "Car Loan", "balance": 5206}
        ])

    if budget_col.count_documents({}) == 0:
        budget_col.insert_one({
            "monthly_income": 3397,
            "expenses": {
                "mortgage": 904,
                "property tax": 334,
                "gas": 100,
                "home insurance": 130,
                "food": 650,
                "car loan": 340,
                "credit cards": 400,
                "meds": 50,
                "oil changes": 30,
                "holidays/car registration": 242,
                "ChatGPT": 20,
                "Lot rent": 360,
                "retirement 5%": 243
            }
        })
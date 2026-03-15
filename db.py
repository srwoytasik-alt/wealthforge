import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env locally
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)

db = client["wealthforge"]


def get_collection(name):
    return db[name]


def seed_data():

    assets_col = db["assets"]
    debts_col = db["debts"]
    budget_col = db["budget"]

    # -------------------------
    # Assets
    # -------------------------

    if assets_col.count_documents({}) == 0:

        assets_col.insert_many([

            {"name": "Emergency Fund", "value": 20, "type": "liquid"},

            {"name": "Home Value", "value": 268000, "type": "illiquid"},

            {"name": "Toyota Corolla", "value": 7000, "type": "illiquid"},

            {"name": "Ford Truck", "value": 3500, "type": "illiquid"},

            {"name": "Trailer", "value": 6500, "type": "illiquid"}

        ])

    # -------------------------
    # Debts
    # -------------------------

    if debts_col.count_documents({}) == 0:

        debts_col.insert_many([

            {"name": "Mortgage", "balance": 168000},

            {"name": "Credit Cards", "balance": 40000},

            {"name": "Student Loan", "balance": 12000},

            {"name": "Car Loan", "balance": 5206}

        ])

    # -------------------------
    # Budget
    # -------------------------

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
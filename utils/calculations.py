def calculate_net_worth(assets, debts):

    asset_total = sum(a.get("value", 0) for a in assets)
    debt_total = sum(d.get("balance", 0) for d in debts)

    return asset_total - debt_total


def calculate_surplus(budget):

    total_exp = sum(budget.get("expenses", {}).values())

    return budget.get("monthly_income", 0) - total_exp


def calculate_liquid_assets(assets):

    return sum(
        a.get("value", 0)
        for a in assets
        if a.get("type") == "liquid"
    )


def calculate_illiquid_assets(assets):

    return sum(
        a.get("value", 0)
        for a in assets
        if a.get("type") == "illiquid"
    )


def calculate_savings_rate(transactions):

    income = sum(t["amount"] for t in transactions if t["type"] == "Income")

    expenses = sum(t["amount"] for t in transactions if t["type"] == "Expense")

    if income == 0:
        return 0

    return (income - expenses) / income
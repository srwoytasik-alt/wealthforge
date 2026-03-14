def calculate_net_worth(assets, debts):
    asset_total = sum(a.get("value", 0) for a in assets)
    debt_total = sum(d.get("balance", 0) for d in debts)
    return asset_total - debt_total

def calculate_surplus(budget):
    total_exp = sum(budget.get("expenses", {}).values())
    return budget.get("monthly_income", 0) - total_exp
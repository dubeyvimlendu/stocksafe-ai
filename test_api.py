from stock_data import get_company_history, get_company_info

symbol = "TCS"

print("=== BASIC INFO ===")
info = get_company_info(symbol)
print(info.get("longName"))
print("Market Cap:", info.get("marketCap"))
print("PE Ratio:", info.get("trailingPE"))
print("Sector:", info.get("sector"))

print("\n=== PRICE DATA (HEAD) ===")
history = get_company_history(symbol)
print(history.head())

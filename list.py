import pandas as pd

def load_company_list():
    df = pd.read_csv("companies.csv")

    # We know the symbol column exists
    symbols = df["Symbol"].dropna().unique().tolist()
    symbols = [s.strip().upper() for s in symbols]

    # Company names (optional)
    names = df["Company Name"].dropna().tolist()

    return symbols, names, df

symbols, names, full_company_df = load_company_list()

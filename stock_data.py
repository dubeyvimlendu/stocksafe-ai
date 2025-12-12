import yfinance as yf

def format_symbol(symbol):
    if not symbol.endswith(".NS"):
        return symbol + ".NS"
    return symbol

def get_company_history(symbol, period="5y"):
    symbol = format_symbol(symbol)
    stock = yf.Ticker(symbol)
    return stock.history(period=period)

def get_company_info(symbol):
    symbol = format_symbol(symbol)
    stock = yf.Ticker(symbol)
    return stock.info

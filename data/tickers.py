import pandas as pd

# Tickers
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
sp500_tickers = {name: symbol for symbol, name in zip(sp500_tickers['Symbol'], sp500_tickers['Security'])}
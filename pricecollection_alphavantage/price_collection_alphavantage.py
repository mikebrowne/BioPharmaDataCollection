'''

pricecollection_alphavantage.py

A wrapper function to collect (and save) daily adjusted pricing data for a watchlist
of public stock.

Developer: Michael Browne
Email: mikelcbrowne@gmail.com

'''

import os
import pandas as pd
import datetime as dt
from alpha_vantage.timeseries import TimeSeries
from tqdm import tqdm
import time


class UpdatePriceData:
    def __init__(self, ticker_list, api_key, fpath=None):
        self.ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
        self.fpath = fpath
        self.missed_tickers = []

        self.df = self.open_csv()

        self.ticker_list = self.filter_tickers(ticker_list)
        self.get_new_data_multiple_stock()

        self.save_csv()

    def open_csv(self):
        if self.fpath is None:
            return pd.DataFrame()

        try:
            return pd.read_csv(self.fpath, index_col=0)
        except Exception as e:
            return pd.DataFrame()

    def save_csv(self):
        if self.fpath is not None:
            try:
                self.df.to_csv(self.fpath)
            except Exception as e:
                print(str(e))

    def filter_tickers(self, tickers):
        return list(set(tickers) - set(self.df.index))

    def get_new_data_single_stock(self, ticker):
        data, _ = self.ts.get_daily_adjusted(ticker.upper(), outputsize="full")
        return data["5. adjusted close"].to_frame(ticker)

    def get_new_data_multiple_stock(self):
        for i, ticker in enumerate(tqdm(self.ticker_list)):
            try:
                if i % 5 == 0:
                    time.sleep(65)  # Should wait 60 seconds for the API, but chose 65 to be on the safe side
                self.df = pd.concat([self.df, self.get_new_data_single_stock(ticker)], axis=1, sort=False)
            except Exception as e:
                # print(str(e))
                self.missed_tickers.append(ticker)


if __name__ == "__main__":
    with open("../AlphaVantageAPI.txt", "r") as doc:
        api_key = doc.read()

    nasdaq_watchlist = pd.read_csv("../Data/watchlist_nasdaq_feb262019.csv")
    nasdaq_watchlist.columns = ["CompanyName", "Ticker", "MarketCap", "Sector", "Exchange"]

    # Choose a subset of the companies
    watchlist_in_scope = nasdaq_watchlist.loc[nasdaq_watchlist.MarketCap.between(500, 5000, inclusive=True)]

    tickers = list(watchlist_in_scope.Ticker.values)

    updater = UpdatePriceData(tickers, api_key, "../Data/stock_prices_asof_2019-06-21.csv")

    print(updater.missed_tickers)
'''

businesswirescraper.py

Module holding the class:
    BusinessWireScraper

Developer: Michael Browne
    Email: mikelcbrowne@gmail.com

'''
import pandas as pd
from utility import clean_name


class DataScraper:
    def __init__(self, watchlist, filepath, num_process=3, max_batch_size=3, num_pages=1):
        self.watchlist = watchlist
        self.filepath = filepath
        self.num_process = num_process
        self.max_batch_size = max_batch_size
        self.num_pages = num_pages

    def run(self):
        pass

    def _single_batch__(self, subset):
        pass

    def _data_scrape_manager__(self, subset):
        pass

    def _scrape_individual_data__(self, company_name, ticker, browser):
        pass


if __name__== "__main__":
    # Test the functionality
    nasdaq_watchlist = pd.read_csv("../Data/watchlist_nasdaq_feb262019.csv")
    nasdaq_watchlist.columns = ["CompanyName", "Ticker", "MarketCap", "Sector", "Exchange"]
    nasdaq_watchlist["CompanyName"] = nasdaq_watchlist.CompanyName.apply(clean_name)

    # Choose a subset of the companies
    watchlist_in_scope = nasdaq_watchlist.loc[nasdaq_watchlist.MarketCap.between(100, 1000, inclusive=True)].iloc[:20]

    print("Collecting data for {} companies".format(watchlist_in_scope.shape[0]), "\n")

    # fill in as I go

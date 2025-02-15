'''

businesswirescraper.py

Module holding the class:
    BusinessWireScraper

Developer: Michael Browne
    Email: mikelcbrowne@gmail.com

'''
import pandas as pd
import numpy as np
import os
from multiprocessing import Pool
from selenium import webdriver
from utility_functions import clean_name, open_file
from scraper_functionality import scrape_search_pages, scrape_articles


class DataScraper:
    def __init__(self, watchlist, file_path, num_process=3, max_batch_depth=3, num_pages=1):
        self.watchlist = watchlist
        self.file_path = file_path
        self.num_process = num_process
        self.max_batch_depth = max_batch_depth
        self.num_pages = num_pages
        self.file_name = os.path.join(self.file_path, "business_wire_scrape_results.csv")

        # Chrome driver settings
        self.chromedriver = "chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = self.chromedriver

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1200x600')

    def run(self):
        batch_size = self.max_batch_depth * self.num_process

        for i in range(0, self.watchlist.shape[0], batch_size):
            print("Starting batch {}...".format(i))

            new_data = self._single_batch__(self.watchlist.iloc[i:i + batch_size])

            if len(new_data) > 0:
                new_df = pd.concat(new_data)
                old_df = open_file(self.file_name)

                pd.concat([old_df, new_df], sort=False).to_csv(self.file_name)

    def _single_batch__(self, subset):
        '''Splits the data into processes and runs the scraper on each process'''
        n = np.ceil(subset.shape[0] / self.num_process).astype(int)  # chunk batch into sub sets for pooling
        subset_watchlist = [subset.iloc[i:i + n] for i in range(0, subset.shape[0], n)]

        print("\tLength of each subset:")
        print("\t", [i.shape[0] for i in subset_watchlist])

        pool = Pool(processes=self.num_process)

        # TODO this may give an issue since now the function takes 2 values in, will have to check the pool docs
        results = pool.map(self._data_scrape_manager__, subset_watchlist)

        res_combined = []
        for res in results:
            if len(res) > 0:
                res_combined = res_combined + res

        return res_combined

    def _data_scrape_manager__(self, subset):
        '''
        Scrapes the data for a set of companies
        :param subset: (Pandas df) - Dataframe containing columns: company_name, ticker
        :return: (list) - list of dataframes for each company
        '''
        # Set up the browser to initialize scrape
        browser = webdriver.Chrome(executable_path=self.chromedriver, chrome_options=self.options)

        list_frames = []
        for ind, row in subset.iterrows():
            try:
                list_frames.append(self._scrape_individual_data__(row.CompanyName, row.Ticker, browser))
            except Exception as e:
                print(str(e))

            print("\tCompleted scrape for", row.CompanyName)

        browser.close()

        return list_frames

    def _scrape_individual_data__(self, company_name, ticker, browser):
        result_df = scrape_search_pages(company_name, browser, self.num_pages)
        result_df["article"] = scrape_articles(result_df.link.values, browser)
        result_df["ticker"] = [ticker] * result_df.shape[0]

        return result_df


if __name__ == "__main__":
    # Test the functionality
    nasdaq_watchlist = pd.read_csv("../Data/watchlist_nasdaq_feb262019.csv")
    nasdaq_watchlist.columns = ["CompanyName", "Ticker", "MarketCap", "Sector", "Exchange"]
    nasdaq_watchlist["CompanyName"] = nasdaq_watchlist.CompanyName.apply(clean_name)

    # Choose a subset of the companies
    watchlist_in_scope = nasdaq_watchlist.loc[nasdaq_watchlist.MarketCap.between(500, 5000, inclusive=True)]

    print("Collecting data for {} companies".format(watchlist_in_scope.shape[0]), "\n")

    scraper = DataScraper(watchlist_in_scope, "", num_process=5, max_batch_depth=3, num_pages=5)
    scraper.run()


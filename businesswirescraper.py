# Imports
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import pandas as pd
import os
import numpy as np
from multiprocessing import Pool
import re

# Settings
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

chromedriver = "chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')


# Set file name
def file_name():
    # This will later be a global attribute for the class
    return "clinical_trial_results_business_wire.csv"


def scrape(url, browser):
    try:

        soup = get_page_as_soup(url, browser)

        section = soup.find(class_="bw-release-story")
        s = section.text
        s = re.sub('\s+', ' ', s)
        return s

    except Exception as e:
        print("Could not scrape the data for : ", url)
        print("\t", str(e))


def page_url(company_name, page_number):
    '''
    Get's the URL for the search page of a company
    :param company_name: (str)
    :param page_number: (int)
    :return: (str) - Formatted URL
    '''
    company_name = company_name.replace(" ", "%20")
    url_template_1 = r"https://www.businesswire.com/portal/site/home/search"
    url_template_2 = r"/?searchType=news&searchTerm={}&searchPage={}"
    return (url_template_1 + url_template_2).format(company_name, page_number)


def get_page_as_soup(url, browser):
    '''
    Returns a BeautifulSoup object from a URL
    :param url: (str) - URL link to a web page
    :param browser: (obj) - Selenium Webdriver object
    :return: (obj) - BeautifulSoup object
    '''
    browser.get(url)

    time.sleep(np.random.randint(1, 6))

    content = browser.page_source

    soup = BeautifulSoup(content, "lxml")
    return soup


def get_content(company, browser, num_pages=1):

    soups = {}  # The key will be the page number, the value will be the data
    if num_pages == "all":
        # First get the number of pages
        first_page_url = page_url(company, 1)
        first_page_soup = get_page_as_soup(first_page_url, browser)
        results = first_page_soup.find(class_="bw-search-results")
        num_pages = int(results.find_all("div")[-1].find_all("a")[-1].text)

    # Iterate through the pages and get the soup objects
    for i in range(1, num_pages + 1):
        try:
            url = page_url(company, i)
            soups[i] = get_page_as_soup(url, browser)
        except Exception as e:
            # Note: Will build in a better system here for exception handling...
            print("Scraper failed for {} on page: {}.".format(company, i))
            print("\t", str(e))
    return soups


def list_item_to_data(li):
    return {
        "time": li.time.text,
        "title": li.h3.text,
        "link": li.a["href"]
    }


def soup_to_list_items(soup):
    results = soup.find(class_="bw-search-results")
    list_items = results.find_all("li")
    return list(list_items)


def soup_to_data(soup_dict):
    list_items = []
    for i in soup_dict:
        list_items += soup_to_list_items(soup_dict[i])
    return {i: list_item_to_data(li) for i, li in enumerate(list_items)}


def items_to_df(dict_items):
    return pd.DataFrame(dict_items).T


def search_for_clinical_information(df):
    try:
        return df.loc[df.title.str.contains("clinical|Clinical")]
    except Exception as e:
        print("Empty DataFrame", str(e))
        return pd.DataFrame(columns=["link", "time", "title", "ticker", "article"])


def open_file(f_name):
    if os.path.isfile('clinical_trial_results_business_wire.csv'):
        return pd.read_csv(f_name, index_col=0)
    else:
        return pd.DataFrame(columns=["link", "time", "title", "ticker", "article"])


def save_file(df, f_name):
    df.to_csv(f_name)


def scrape_clinical_data(company_name, ticker, browser, num_pages=1):
    s = get_content(company_name, browser, num_pages)
    d = soup_to_data(s)
    df = items_to_df(d)
    df["article"] = [scrape(url, browser) for _, url in df.link.iteritems()]
    df["ticker"] = [ticker] * df.shape[0]
    return df


def add_to_data(new_df):
    df = open_file(file_name())
    df = pd.concat([df, new_df], axis=0, sort=False)
    df.drop_duplicates(inplace=True)
    save_file(df, file_name())


def scrape_multiple_clinical_data(company_information):
    # Note the input is a data frame, we need the columns: company_name, ticker
    try:
        browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
        list_frames = []
        if len(company_information.index) > 1:
            print("Starting scraper for sub-set : ", company_information.index[0], " to ", company_information.index[1])
        else:
            print("Starting scraper for sub-set : ", company_information.index[0])
        print("-------------")
        for ind, row in company_information.iterrows():
            list_frames.append(scrape_clinical_data(row.CompanyName, row.Ticker, browser, 5)) # NOTE will need to change the
                                                                                              # num of pages here later
            print("Completed scrape for", row.CompanyName)

        browser.close()

        return list_frames
    except Exception as e:
        print(str(e))
        return []


# Clean names
def clean_name(name):
    name = name.lower()
    name = name.replace("inc", "")
    name = name.replace(".", "")
    name = name.replace(",", "")
    name = name.strip()
    return name


def format_result(res):
    return pd.concat([pd.concat(item, axis=0, sort=False) for item in res], axis=0, sort=False)


def single_batch(data, num_processes):
    # Split into 5 groups
    n = np.ceil(data.shape[0] / num_processes).astype(int)  #chunk row size
    sub_set_watchlist = [data.iloc[i:i+n] for i in range(0, data.shape[0], n)]

    print("Length of each subset:")
    print([i.shape[0] for i in sub_set_watchlist])

    pool = Pool(processes=num_processes)

    results = pool.map(scrape_multiple_clinical_data, sub_set_watchlist)

    res_combined = []
    for res in results:
        if len(res) > 0:
            res_combined = res_combined + res

    return res_combined


def batch_process(data, max_batch_size, num_processes, filename):
    # Split the data into sets of max_batch_size x num_processes
    n = max_batch_size * num_processes
    print("Each batch has up to {} items".format(n))
    m = np.ceil(data.shape[0] / n).astype(int)

    print("There will be {} batches".format(m))

    for i in range(0, data.shape[0], n):
        print("\tStarting batch {}...".format(i))

        new_data = single_batch(data.iloc[i:i + n], num_processes)
        if len(new_data) > 0:
            new_df = pd.concat(new_data)
            old_df = pd.read_csv(filename, index_col=0)

            pd.concat([old_df, new_df]).to_csv(filename)


def main():
    nasdaq_watchlist = pd.read_csv("Data/watchlist_nasdaq_feb262019.csv")
    nasdaq_watchlist.columns = ["CompanyName", "Ticker", "MarketCap", "Sector", "Exchange"]

    nasdaq_watchlist["CompanyName"] = nasdaq_watchlist.CompanyName.apply(clean_name)

    # Choose a subset of the companies
    watchlist_in_scope = nasdaq_watchlist.loc[nasdaq_watchlist.MarketCap.between(100, 1000, inclusive=True)]

    print("Collecting data for {} companies".format(watchlist_in_scope.shape[0]), "\n")

    # Set the number of processes
    num_processes = 5

    filename="trial_run_data_scraper.csv"

    if filename not in os.listdir():
        pd.DataFrame().to_csv(filename)

    batch_process(watchlist_in_scope, max_batch_size=3, num_processes=num_processes, filename=filename)

    df = pd.read_csv(filename, index_col=0)

    print(df)


if __name__ == "__main__":
    main()
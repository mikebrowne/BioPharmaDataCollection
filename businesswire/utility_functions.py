'''

utility_functions.py

Various helper functions for use in the data scraper.

'''
from bs4 import BeautifulSoup
import time
import numpy as np
import os
from pandas import read_csv, DataFrame


def clean_name(name):
    '''Helper function to clean the name before use.'''
    name = name.lower()
    name = name.replace("inc", "")
    name = name.replace(".", "")
    name = name.replace(",", "")
    name = name.strip()
    return name


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


def open_file(f_name):
    if os.path.isfile(f_name):
        return read_csv(f_name, index_col=0)
    else:
        return DataFrame(columns=["link", "time", "title", "ticker", "article"])


def save_file(df, f_name):
    df.to_csv(f_name)
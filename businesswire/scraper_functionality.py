'''

scraper_functionality.py

Module contains the functions used to implement the data scraper. The public functions are:
    * scrape_search_pages()
    * scrape_articles

Developer: Michael Browne
Email: mikelcbrowne@gmail.com

'''

# IMPORTS
import pandas as pd
from bs4 import BeautifulSoup
import time
import numpy as np
import re


# PUBLIC FUNCTIONS
def scrape_search_pages(company_name, browser, num_pages=1):
    soups = get_search_pages(company_name, browser, num_pages=1)
    return pd.DataFrame(soups_to_data(soups)).T


# PRIVATE HELPER FUNCTIONS
def scrape_articles(article_links, browser):
    return [scrape_individual_article(url, browser) for url in article_links]


def get_search_pages(company_name, browser, num_pages):
    soups = {}  # The key will be the page number, the value will be the data
    if num_pages == "all":
        # First get the number of pages
        first_page_url = page_url(company_name, 1)
        first_page_soup = get_page_as_soup(first_page_url, browser)
        results = first_page_soup.find(class_="bw-search-results")
        num_pages = int(results.find_all("div")[-1].find_all("a")[-1].text)

    # Iterate through the pages and get the soup objects
    for i in range(1, num_pages + 1):
        try:
            url = page_url(company_name, i)
            soups[i] = get_page_as_soup(url, browser)
        except Exception as e:
            # Note: Will build in a better system here for exception handling...
            print("Scraper failed for {} on search page: {}.".format(company_name, i))
            print("\t", str(e))
    return soups


def soups_to_data(soup_dict):
    list_items = []
    for i in soup_dict:
        list_items += soup_to_list_items(soup_dict[i])
    return {i: list_item_to_data(li) for i, li in enumerate(list_items)}


def soup_to_list_items(soup):
    results = soup.find(class_="bw-search-results")
    list_items = results.find_all("li")
    return list(list_items)


def list_item_to_data(li):
    return {
        "time": li.time.text,
        "title": li.h3.text,
        "link": li.a["href"]
    }


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


def scrape_individual_article(url, browser):
    try:
        soup = get_page_as_soup(url, browser)
        section = soup.find(class_="bw-release-story")
        s = section.text
        s = re.sub('\s+', ' ', s)
        return s

    except Exception as e:
        print("Could not scrape the article data for : ", url)
        print("\t", str(e))
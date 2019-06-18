'''

utility.py

Various helper functions for use in the data scraper.

'''


def clean_name(name):
    '''Helper function to clean the name before use.'''
    name = name.lower()
    name = name.replace("inc", "")
    name = name.replace(".", "")
    name = name.replace(",", "")
    name = name.strip()
    return name
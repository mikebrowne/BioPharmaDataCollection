# BioPharmaDataCollection

Various data scrapers used to collect data regarding companies on the public markets.

## Usage

```python
from businesswire/businesswirescraper import DataScraper

PATH_TO_WATCHLIST = # Insert the path to your watch list as a csv file here. Note that the csv should have ATLEAST the column names
                    # "CompanyName" and "Ticker"
                    
OUTPUT_PATH = # Insert the path to the folder you would like the output file located

watchlist = pd.read_csv(PATH_TO_WATCHLIST)

scraper = DataScraper(watchlist, OUTPUT_PATH, num_process=5, max_batch_depth=3, num_pages=5)
scraper.run()

```


import os
#import urllib3
try:
    import requests
    from bs4 import BeautifulSoup
    print("Import successful")
except ImportError:
    print("Module error detected\n")
    print("\'py -m pip install requests beautifulsoup4 --user \': copy and run code in cmd to install required packages\n")

_URL = "https://jmedicalcasereports.biomedcentral.com"
urls = []
names = []

# c-listing__title

pgs = int(input("Pages to scan : (1 - 148) : "))

for pg in range(1, pgs+1):
    URL = "https://jmedicalcasereports.biomedcentral.com/articles?tab=keyword&searchType=journalSearch&sort=PubDateAscending&page=" + \
        str(pg)

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    res = soup.find_all('ul', "c-listing__view-options")

    for i in res:
        x = i.find('a')
        _FULLURL = _URL + x.get('href')
        _FULLURL = _FULLURL.replace('articles', 'track/pdf')
        urls.append(_FULLURL)

    print("Page {} done. Processed {} urls.".format(pg, len(urls)))

with open('out.txt', "w", encoding="utf-8") as f:
    f.write("{}".format("\n".join(urls)))

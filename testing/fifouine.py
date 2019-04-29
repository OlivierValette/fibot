from bs4 import BeautifulSoup
import requests

# test url to scrape from
target = 'http://www.morningstar.fr/fr/funds/snapshot/snapshot.aspx?id=F0GBR04QCM'

# fetch the content from the url, using the requests library
# use the html parser to parse the url content and store it in a variable
page_response = requests.get(target, timeout=5)
page_content = BeautifulSoup(page_response.content, "html.parser")

print(page_content.prettify())

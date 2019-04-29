import requests
import mysql.connector

config = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'fundlog',
  'raise_on_warnings': True
}

# connect to fundlog db
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

query = "SELECT name, search_url, fund_url FROM source"
cursor.execute(query)
s_url = {}
f_url = {}
for (name, search_url, fund_url) in cursor:
    s_url[name] = search_url
    f_url[name] = fund_url
print(s_url)
print(f_url)
cursor.close()
cnx.close()

# test url to scrape from
MS_FUND_URL = f_url["morningstar"]
ms_id = 'F0GBR04QCM'
ms_tab = '1'
target = MS_FUND_URL + ms_id
if ms_tab:
    target += '&tab=' + ms_tab
print(target)
# fetch the content from the url, using the requests library
page = requests.get(target, timeout=5)
# save the content of the page for testing purpose
if page.status_code == 200:
    filename = 'pages/ms' + ms_tab + '.html'
    with open(filename, 'wb') as f:
        f.write(page.content)
        f.close()
else:
    print("Erreur d'accès à la page web, code " + page.status_code)

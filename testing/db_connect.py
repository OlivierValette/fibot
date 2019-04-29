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

query = "SELECT name, url FROM source"
cursor.execute(query)
target = {}
for (name, url) in cursor:
    target[name] = url
print(target)
cursor.close()
cnx.close()

# test url to scrape from
MS_FUND_URL = 'http://www.morningstar.fr/fr/funds/snapshot/snapshot.aspx?id='
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

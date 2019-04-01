import requests

# test url to scrape from
QS_FUND_URL = "http://www.quantalys.com/Fonds/"
qs_id = '15111'
target = QS_FUND_URL
# qs_tab = 'Performances'
qs_tab = ''
if qs_tab:
    target += qs_tab + '/' + qs_id
else:
    target += qs_id
print(target)
# fetch the content from the url, using the requests library
page = requests.get(target, timeout=5)
# save the content of the page for testing purpose
if page.status_code == 200:
    filename = 'pages/qs' + qs_tab + '.html'
    with open(filename, 'wb') as f:
        f.write(page.content)
        f.close()
else:
    print("Erreur d'accès à la page web, code " + page.status_code)

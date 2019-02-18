import requests
from bs4 import BeautifulSoup

# TODO: parameter to be stored in the database
QS_SEARCH_URL = "http://www.quantalys.com/search/listefonds.aspx?autobind=1&autoredirect=1&ISINorNom="


# Search for an asset's Quantalys ID given its exact ISIN
def find_qs_id_by_isin(id):

    target = QS_SEARCH_URL + id

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")

        # seek for: <input id="id-produit" type="hidden" value="70584">
        tag = pagecontent.find('input', id='id-produit')
        return tag['value']
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Quantalys")
        return -1


qsid = find_qs_id_by_isin("FR0000284689")
print("Quantalys id :", qsid)

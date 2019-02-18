import requests
from bs4 import BeautifulSoup

# TODO: parameter to be stored in the database
QS_FUND_URL = "http://www.quantalys.com/Fonds/"


# Get an asset's Quantalys data given its exact Quantalys Id
def get_qs_info(qs_id):

    target = QS_FUND_URL + qs_id

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")

        # seek for:
        # <input id="id-produit" type="hidden" value="70584">
        #    <input id="id-cat" type="hidden" value="29">
        #     <input id="id-bench" type="hidden" value="2647">
        #
        tag = pagecontent.find('input', id='id-cat')
        return tag['value']
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Quantalys")
        return -1


cat_id = get_qs_info("70584")
print("Quantalys id : 70584 --> category id :", cat_id)

import requests
from bs4 import BeautifulSoup

# TODO: parameter to be stored in the database
MS_SEARCH_URL = "http://www.morningstar.fr/fr/funds/SecuritySearchResults.aspx?search="


# Search for an asset's Morningstar ID given its exact ISIN
def find_ms_id_by_isin(id):

    target = MS_SEARCH_URL + id

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")
        # seek for <a href="/fr/funds/snapshot/snapshot.aspx?id=F00000MNJW">Comgest Monde I</a>
        # under a <td class="msDataText searchLink">
        # for link in pagecontent.find_all("td", "searchLink"):
        link = pagecontent.find("td", "searchLink")
        return link.children.__next__().get('href')[-10:]
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Morningstar")
        return -1


msid = find_ms_id_by_isin("FR0011007251")
print(msid)

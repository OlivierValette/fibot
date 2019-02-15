import requests
from bs4 import BeautifulSoup

# TODO: parameter to be stored in the database
MS_SEARCH_URL = "http://www.morningstar.fr/fr/funds/SecuritySearchResults.aspx?search="


# Search for an asset's Morningstar ID
def findMsIdByLabel(label):

    target = MS_SEARCH_URL + label

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")
        # seek for <a href="/fr/funds/snapshot/snapshot.aspx?id=F00000MNJW">Comgest Monde I</a>
        # under a <td class="msDataText searchLink">
        results = []
        for link in pagecontent.find_all("td", "searchLink"):
            results.append(link.children.__next__().get('href')[-10:])
            results.append(link.children.__next__().get_text())
        for link in pagecontent.find_all("td", "searchIsin"):
            results.append(link.children.__next__().get_text())
        return results
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Morningstar")
        return -1


msid = findMsIdByLabel("Comgest Monde")
print(msid)

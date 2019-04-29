import requests
from bs4 import BeautifulSoup

# TODO: parameter to be stored in the database
QS_SEARCH_URL = "http://www.quantalys.com/search/listefonds.aspx?autobind=1&autoredirect=1&ISINorNom="


def find_qs_id_by_label(label):
    """
    Search for an asset's Quantalys ID given a label (limited to 25 results)
    :param label: portion of text
    :return: list of dictionaries isin / label / Quantalys id
    """
    target = QS_SEARCH_URL + label

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")

        # Les résultats sont dans un tableau d'id="Contenu_Contenu_selectFunds_listeFonds"
        # <table (etc.) id="Contenu_Contenu_selectFunds_listeFonds" (etc.)>
        #
        # <tr class="row_table_search_result" or "alt_row_table_search_result">
        #   (...)
        #   <td align="left">
        #       <a title="29 HAUSSMANN EURO RENDEMENT C - FR0010902726" href="/Produit/131744">
        #           29 HAUSSMANN EURO RENDEMENT
        #       </a>
        #   </td>
        #   (...)
        # </tr>

        table = pagecontent.find_all('table', id="Contenu_Contenu_selectFunds_listeFonds")[0]
        table_lines = table.find_all('tr')
        search_results = []
        for i in range(1, len(table_lines)-2):
            search_results.append({
                'isin': table_lines[i].a.get('title').split()[-1],
                'label': table_lines[i].a.text,
                'id': table_lines[i].a.get('href').split('/')[-1]
            })
        return search_results
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Quantalys")
        return -1


msid = find_qs_id_by_label("Comgest")
for i in range(0, len(msid)):
    print("i=", i, "-->", msid[i])

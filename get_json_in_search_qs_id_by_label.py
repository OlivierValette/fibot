import requests
from bs4 import BeautifulSoup
import pandas

# TODO: parameter to be stored in the database
QS_SEARCH_URL = "http://www.quantalys.com/search/listefonds.aspx?autobind=1&autoredirect=1&ISINorNom="


# Search for an asset's Quantalys ID from label
def find_qs_id_by_label(label):

    target = QS_SEARCH_URL + label

    # fetch url
    pageresponse = requests.get(target, timeout=5)
    if pageresponse.status_code == 200:
        pagecontent = BeautifulSoup(pageresponse.content, "html.parser")

        # Les résultats sont dans un tableau d'id="Contenu_Contenu_selectFunds_listeFonds"
        # <table (etc.) id="Contenu_Contenu_selectFunds_listeFonds" (etc.)>
        #
        # <tr class="alt_row_table_search_result">
        #   <td style="width:20px;">
        #       <input id="Contenu_Contenu_selectFunds_listeFonds_CheckBoxButton_15"
        #              type="checkbox"
        #              name="ctl00$ctl00$Contenu$Contenu$selectFunds$listeFonds$ctl17$CheckBoxButton"
        #              onclick=(...)
        #        />
        #   </td>
        #   <td title="Fonds" align="center">F</td>
        #   <td align="left">
        #       <a title="29 HAUSSMANN EURO RENDEMENT C - FR0010902726" href="/Produit/131744">
        #           29 HAUSSMANN EURO RENDEMENT
        #       </a>
        #   </td>
        #   <td class="tdnowrap" align="right">1 329,82</td>
        #   <td align="center">EUR</td>
        #   <td> <img src="/images/layout/indicateurs/5p.gif" alt="89 / 100" /></td>
        #   <td class="tdnowrap" align="right" style="color:Green;">3,23%</td>
        #   <td class="tdnowrap" align="right" style="color:Red;">-1,16%</td>
        #   <td class="tdnowrap" align="right" style="color:Green;">11,83%</td>
        #   <td align="center">14/02</td>
        # </tr>

        table = pagecontent.find_all('table', id="Contenu_Contenu_selectFunds_listeFonds")[0]
        df = pandas.read_html(str(table))
        print(df[0].to_string())

        # todo: try using .replace(u"\u00A0", " ")...
        print(df[0].to_json(orient='records'))

        return 1
    else:
        print("Le code saisi ne correspond à aucun fonds référencé par Morningstar")
        return -1


msid = find_qs_id_by_label("Comgest Monde")
print(msid)

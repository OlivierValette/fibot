import time
from slugify import slugify
from bs4 import BeautifulSoup
import pandas
from selenium import webdriver
from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# TODO: parameter to be stored in the database
QS_SEARCH_URL = "http://www.quantalys.com/search/listefonds.aspx?autobind=1&autoredirect=1&ISINorNom="


def find_qs_id_by_label_100(label):
    """
    Search for an asset's Quantalys ID given a label (limited to 100 results)
    Version using Selenium to switch from 25 to 100 results lines
    :param label: portion of text
    :return: list of dictionaries isin / label / Quantalys id
    """
    target = QS_SEARCH_URL + label

    # create a new Firefox session
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(target)
    time.sleep(4)

    # first, close the cookie law box that shadows the targeted dropdown
    # get the input button by its id
    button = driver.find_element_by_id('btnFermer')
    # then click
    button.click()
    time.sleep(4)

    # switch number of results lines from 25 to 100 in dropdown selector:
    # get the dropdown SELECT by its id
    dropdown = Select(driver.find_element_by_id('Contenu_Contenu_selectFunds_listeFonds_pager_ddlPageSize'))
    # select the OPTION with the value 100
    dropdown.select_by_value('100')
    time.sleep(4)

    # back to Beautiful Soup
    pagecontent = BeautifulSoup(driver.page_source, "html.parser")
    # quit webdriver
    driver.quit()

    # process data in BS
    table = pagecontent.find_all('table', id="Contenu_Contenu_selectFunds_listeFonds")[0]
    table_lines = table.find_all('tr')
    search_results = []
    for i in range(1, len(table_lines)-2):
        search_results.append({
            'isin': table_lines[i].a.get('title').split()[-1],
            'label': table_lines[i].a.text,
            'id': table_lines[i].a.get('href').split('/')[-1]
        })

    df = pandas.read_html(str(table))

    filename = slugify("QS_find_" + label, only_ascii=True) + ".json"
    f = open("search_results\\" + filename, "w")
    f.write(df[0].to_json(orient='records'))
    f.close()

    return search_results


msid = find_qs_id_by_label_100("Comgest")
for i in range(0, len(msid)):
    print("i=", i+1, "-->", msid[i])

from config import db_config
import mysql.connector

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import random
from typing import Dict, List, Any

# generate a random user agent
ua = UserAgent()


# Main function
def main():

    # Get a proxies list
    proxies = get_proxies()
    # Choose a proxy
    proxy_index = random_proxy(len(proxies))
    proxy = proxies[proxy_index]

    # Get list of funds to update
    fund_list = get_fund_list()
    print(fund_list)

    # Get list of sources
    source_list = get_source_list()
    print(source_list)

    # Create new funds in fi_info
    cnx = mysql.connector.connect(**db_config)
    cur_ffo = cnx.cursor(buffered=True)
    insert_new_funds = (
        "INSERT INTO fin_info (fund_id, source_id, isin, code) "
        "VALUES (%s, %s, %s, %s)")

    # Iterate through the funds to update list
    for fund in fund_list:
        # get missing source codes
        source_code = find_id_by_isin(fund[1])
        print(source_code)
        # insert new funds for all sources
        for source in source_list:
            # select funds without ffo.id
            if not fund[2]:
                cur_ffo.execute(insert_new_funds, (fund[0], source[0], fund[1], 'UNSET'))
        # Commit the changes
        cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    print(fund_list)

    # Retrieve new funds source codes


# Get a list of proxies
def get_proxies():
    # initialize an empty list for proxies with [ip, port]
    proxies: List[Dict[str, Any]] = []
    # Retrieve latest proxies scraping the site "sslproxies.org"
    url = 'https://www.sslproxies.org/'
    headers = {'user-agent': ua.random}
    proxies_doc = requests.get(url, headers=headers, timeout=5)
    if proxies_doc.status_code == 200:
        soup = BeautifulSoup(proxies_doc.content, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')
        # save proxies in the proxies[] array
        for row in proxies_table.tbody.find_all('tr'):
            proxies.append({
                'ip':   row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })
    else:
        print('Error retrieving proxy list')
    return proxies


# Retrieve a random index proxy
def random_proxy(n):
    return random.randint(0, n - 1)


# Retrieve list of funds to be updated
def get_fund_list():
    cnx = mysql.connector.connect(**db_config)
    # Get two buffered cursors
    cursor = cnx.cursor(buffered=True)
    query = (
        "SELECT fnd.id, fnd.isin, ffo.id, ffo.code "
        "FROM fund AS fnd "
        "LEFT JOIN fin_info AS ffo USING (id) "
        "ORDER BY fnd.id")
    cursor.execute(query)
    fund_list = []
    for row in cursor:
        fund_list.append(row)
    cursor.close()
    cnx.close()
    return fund_list


# Retrieve list of sources
def get_source_list():
    cnx = mysql.connector.connect(**db_config)
    cur_src = cnx.cursor()
    query_src = "SELECT * FROM source"
    cur_src.execute(query_src)
    source_list = []
    for row in cur_src:
        source_list.append(row)
    cur_src.close()
    cnx.close()
    return source_list


# Scrap finance site by ISIN
def page_search_by_isin(url):
    try:
        page_response = requests.get(url, timeout=7)
        page_response.raise_for_status()  # added to catch HTTP errors
    except requests.exceptions.RequestException as e:
        print(e)
        return False
    if page_response.status_code == 200:
        return BeautifulSoup(page_response.content, "html.parser")
    else:
        return False


# Retrieve fund source code by ISIN
# Search for an asset's Morningstar/Quantalys ID given its exact ISIN
def find_id_by_isin(isin):
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    query = "SELECT name, search_url, fund_url FROM source"
    cursor.execute(query)
    code = {}
    for (name, search_url, fund_url) in cursor:
        target = search_url + isin
        page_content = page_search_by_isin(target)
        # default value if an error occurred while requesting page
        code[name] = 'UNSET'
        if page_content:
            if name == "morningstar":
                if page_content.find("td", "searchLink"):
                    code[name] = page_content.find("td", "searchLink").children.__next__().get('href')[-10:]
            else:
                if page_content.find('input', id='id-produit'):
                    code[name] = page_content.find('input', id='id-produit')['value']
    cursor.close()
    cnx.close()
    return code


if __name__ == '__main__':
    main()

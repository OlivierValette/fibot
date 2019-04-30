from config import db_config
import mysql.connector

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import random
from typing import Dict, List, Any

from sfibot import get_info

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
    print(fund_list)                # TODO: remove

    # Get list of sources
    source_list = get_source_list()
    print(source_list)              # TODO: remove

    # Add new funds to fin_info
    cnx = mysql.connector.connect(**db_config)
    cur_ffo = cnx.cursor(buffered=True)
    insert_new_funds = (
        "INSERT INTO fin_info (fund_id, source_id, isin, code) "
        "VALUES (%s, %s, %s, %s)")

    # Iterate through the funds to update list
    for fund in fund_list:
        # get missing source codes
        source_code = find_id_by_isin(fund[1])
        # insert new funds for all sources
        for source in source_list:
            # select funds without ffo.id
            if not fund[2]:
                # get source internal code
                s_code = source_code[source_list[source[0]-1][1]]
                print("updating", s_code)           # TODO: remove
                cur_ffo.execute(insert_new_funds, (fund[0], source[0], fund[1], s_code))
        # Commit the changes
        cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    print(fund_list)                # TODO: remove

    # Retrieve full info for funds with source codes
    cur_ffo = cnx.cursor(buffered=True)         # TODO: is cursor change necessary?
    update_ffo = (
        " UPDATE fin_info AS ffo"
        " SET name = %s, rating = %s, benchmark = %s, lvdate =%s, lvalue = %s, currency = %s,"
        "     date_ytd = %s, perf_a = %s, perf_am1 = %s, perf_am2 = %s, perf_am3 = %s"
        " WHERE ffo.fund_id = %s AND ffo.source_id = %s")
    cur_fnd = cnx.cursor(buffered=True)         # TODO: is cursor change necessary?
    update_fnd = (
        " UPDATE fund AS fnd"
        " SET last_lvalue = %s"
        " WHERE fnd.id = %s")

    # Iterate through the funds to update list
    for fund in fund_list:
        for source in source_list:
            if fund[3] != 'UNSET':
                # scrap info for funds with source codes
                # calling get_info(source.id, source.fund.url, fin_info.code)
                info = get_info(source[0], source[3], fund[3])

                # update fund info in fin_info and fund tables
                if not fund[2]:
                    # get source internal code
                    print("updating", info[0])           # TODO: remove
                    # cur_ffo.execute(update_ffo, (info[5], info[6], info[7], info[8], info[9],
                    print(update_ffo, (info[1], info[2], info[3], info[4], info[5], info[6],
                                       info[7], info[8], info[9], info[10], info[11],
                                       fund[0], source[0]))
                    print(update_fnd, (info[5], fund[0]))
                    # cur_fnd.execute(update_fnd, (info[9], info[1]))

                # Commit the changes
                cnx.commit()


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
# Array of tuples: (fund ID, fund ISIN, fin ID, fin CODE)
def get_fund_list():
    cnx = mysql.connector.connect(**db_config)
    # Get two buffered cursors
    cursor = cnx.cursor(buffered=True)
    query = (
        "SELECT fnd.id, fnd.isin, ffo.id, ffo.code "
        "FROM fund AS fnd "
        "LEFT JOIN fin_info AS ffo ON (ffo.fund_id = fnd.id) "
        "ORDER BY fnd.id")
    cursor.execute(query)
    fund_list = []
    for row in cursor:
        fund_list.append(row)
    cursor.close()
    cnx.close()
    return fund_list


# Retrieve list of sources
# Array of tuples: (ID, NAME, SEARCH_URL, FUND_URL)
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


# Get finance soup by ISIN
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

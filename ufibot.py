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

    fund_list = get_fund_list()
    print(fund_list)

    # create new funds in fi_info
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    insert_new_funds = (
        "INSERT INTO fin_info (fund_id, source_id, isin, code) "
        "VALUES (%s, %s, %s, %s)")

    # Iterate through the result of curA
    for (emp_no, salary, from_date, to_date) in curA:
        # Update the old and insert the new salary
        new_salary = int(round(salary * Decimal('1.15')))
        curB.execute(update_old_salary, (tomorrow, emp_no, from_date))
        curB.execute(insert_new_salary,
                     (emp_no, tomorrow, date(9999, 1, 1, ), new_salary))

        # Commit the changes
        cnx.commit()


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


# Scrap finance site by ISIN
def page_search_by_isin(url):
    page_response = requests.get(url, timeout=5)
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
        if page_content:
            if name == "morningstar":
                code[name] = page_content.find("td", "searchLink").children.__next__().get('href')[-10:]
            else:
                code[name] = page_content.find('input', id='id-produit')['value']
    cursor.close()
    cnx.close()
    return code


if __name__ == '__main__':
    main()

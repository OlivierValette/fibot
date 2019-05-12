# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
from typing import List, Dict, Any

# generate a random user agent
ua = UserAgent()


# Proxies management
def proxies():
    # Get a proxies list
    proxy_list = get_proxies()
    # Choose a proxy
    proxy_index = random_proxy(len(proxy_list))
    return proxy_list[proxy_index]


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


# Get soup
def get_soup(url, delay):
    """
    Return soup of page at url
    :rtype:  BeautifulSoup
    """
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    headers = {'User-Agent': ua}
    try:
        page_response = requests.get(url, timeout=delay, headers=headers)
        page_response.raise_for_status()  # added to catch HTTP errors
    except requests.exceptions.RequestException as e:
        print(e)
        return False
    if page_response.status_code == 200:
        return BeautifulSoup(page_response.content, "html.parser")
    else:
        print('Erreur:', page_response.status_code)
        return False

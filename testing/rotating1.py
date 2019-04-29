from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

# generate a random user agent
ua = UserAgent()
# initialize an empty list for proxies with [ip, port]
proxies = []


# Main function
def main():

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
        print(proxies)
        print(len(proxies))

    else:
        print('Error retrieving proxy list')

    # Choose proxy
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]

    # Generate multiple requests on icanhazip.com to test our proxy
    req = Request('http://icanhazip.com')
    req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')
    for n in range(1, 100):
        # Every 10 requests, generate a new proxy
        if n % 10 == 0:
            proxy_index = random_proxy()
            proxy = proxies[proxy_index]

        try:
            my_ip = urlopen(req).read().decode('utf8')
            print('#' + str(n) + ': ' + my_ip)
        except:  # If error, delete this proxy and find another one
            del proxies[proxy_index]
            print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
            proxy_index = random_proxy()
            proxy = proxies[proxy_index]


# Retrieve a random index proxy
def random_proxy():
    return random.randint(0, len(proxies) - 1)


if __name__ == '__main__':
    main()

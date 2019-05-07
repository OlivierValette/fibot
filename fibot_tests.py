# -*- coding: utf-8 -*-

from scraping import get_soup
from fibot_search import get_info
from fibot_update import get_fund_list, get_source_list, find_code_by_isin, get_currency_list


# Main function
# fibot_tests: test fibot components
def main():

    # Test morningstar connection

    # Get list of sources
    # source_list = get_source_list()
    # print("sources list:", source_list)
    # ms_url = source_list[0]['search_url']
    # isin = 'FR0000284689'
    # code = find_code_by_isin(isin, 'morningstar', ms_url)
    # print(code)

    # Test currency
    currency_list = get_currency_list()
    print(currency_list)
    test_cur = 'USD'
    currency_id = False
    for currency in currency_list:
        if currency['code'] == test_cur:
            currency_id = currency['id']
    print(currency_id)


if __name__ == '__main__':
    main()

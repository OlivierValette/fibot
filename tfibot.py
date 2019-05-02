# -*- coding: utf-8 -*-

from scraping import get_soup
from sfibot import get_info
from ufibot import get_fund_list, get_source_list, find_code_by_isin


# Main function
# tfibot: test fibot components
def main():

    # Test morningstar connection

    # Get list of sources
    source_list = get_source_list()
    print("sources list:", source_list)
    ms_url = source_list[0]['search_url']
    isin = 'FR0000284689'
    code = find_code_by_isin(isin, 'morningstar', ms_url)
    print(code)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
from datetime import datetime
from fibot_search import get_info
from fibot_update import get_source_list

# Set list of funds to test
isin = 'FR0000284689'
fund_test1 = {
    'source_id': '1',
    'fund_url': 'http://www.morningstar.fr/fr/funds/SecuritySearchResults.aspx?search=',
    'code': 'F0GBR04QCM'
}
fund_test2 = {
    'source_id': '2',
    'fund_url': 'http://www.quantalys.com/search/listefonds.aspx?autobind=1&autoredirect=1&ISINorNom=',
    'code': 'F0GBR04QCM'
}


def testufibot(ufibot):
    assert ufibot(fund_test1) ==



# calling get_info(source.id, source.fund.url, fin_info.code)
def ufibot(fund):
    source = source_list[fund['source_id'] - 1]
    print("calling get_info(", fund['source_id'], ",", source['fund_url'], ",", fund['code'], ")")
    info = get_info(fund['source_id'], source['fund_url'], fund['code'])
    print(info)
    if len(info) > 1:
        # converting date formats from DD/MM/YYYY to YYYYY-MM-DD
        info['lvdate'] = datetime.strptime(info['lvdate'], "%d/%m/%Y").strftime("%Y-%m-%d")
        info['date_ytd'] = datetime.strptime(info['date_ytd'], "%d/%m/%Y").strftime("%Y-%m-%d")
        # converting float formats from , to .
        info['lvalue'] = float(str(info['lvalue']).replace(',', '.').replace(' ', ''))
        info['perf_a'] = float(str(info['perf_a']).replace(',', '.').replace(' ', ''))
        info['perf_am1'] = float(str(info['perf_am1']).replace(',', '.').replace(' ', ''))
        info['perf_am2'] = float(str(info['perf_am2']).replace(',', '.').replace(' ', ''))
        info['perf_am3'] = float(str(info['perf_am3']).replace(',', '.').replace(' ', ''))
        # retrieving currency id and value
        currency_list = get_currency_list()
        print(currency_list)
        currency_id = False
        currency_value = 1.
        for currency in currency_list:
            if currency['code'] == info['currency']:
                currency_id = currency['id']
                currency_value = currency['value']
        print('selected currency:', currency_id, currency_value)
        if not currency_id:
            currency_id = 1     # if not in currency, default set to EUR, TODO: improve
        # update fund info in fin_info
        print("updating", info['code'])           # TODO: remove
        print(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'],
                           currency_id, info['date_ytd'], info['perf_a'], info['perf_am1'],
                           info['perf_am2'], info['perf_am3'], fund['id'], fund['source_id']))
        # update fund table with last-lvalue (converted in euros)
        lvalue = info['lvalue'] / currency_value
        print(update_fnd, (lvalue, fund['id']))

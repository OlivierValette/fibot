# -*- coding: utf-8 -*-
from datetime import datetime
import mysql.connector
from config import db_config
from scraping import get_soup
from sfibot import get_info
from afibot import get_historical_values


# Main function
# fibot: update financial data in "fin_info" by scraping sites in "source"
def main():

    # Get list of funds to update (only active funds in "funds")
    fund_list = get_fund_list()
    print("funds list:", fund_list)                # TODO: remove
    # Get list of sources
    source_list = get_source_list()
    print("sources list:", source_list)              # TODO: remove

    # PART I - Add new funds to table "fin_info"
    # ------------------------------------------
    cnx = mysql.connector.connect(**db_config)
    cur_ffo = cnx.cursor(buffered=True)
    insert_new_funds = (
        "INSERT INTO fin_info (fund_id, source_id, isin, code) "
        "VALUES (%s, %s, %s, %s)")
    # Iterate through the funds
    for fund in fund_list:
        # select funds no fin_info.id found
        if not fund['fin_id']:
            # scanning all sources
            for source in source_list:
                # get source internal code
                source_code = find_code_by_isin(fund['isin'], source['name'], source['search_url'])
                cur_ffo.execute(insert_new_funds, (fund['id'], source['id'], fund['isin'], source_code))
            # Commit the changes
            cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    print("updated funds list:", fund_list)                # TODO: remove

    # PART II - Update source code when still "UNSET"
    # -----------------------------------------------
    cnx = mysql.connector.connect(**db_config)
    cur_ffo = cnx.cursor(buffered=True)
    update_ffo = (
        " UPDATE fin_info AS ffo"
        " SET code = %s"
        " WHERE fund_id = %s and source_id = %s")
    # Iterate through the funds
    for fund in fund_list:
        # select funds with source code 'UNSET'
        if fund['code'] == 'SKIP':   # temporary skipping this part  SKIP->UNSET
            # new attempt to get source internal code
            source = source_list[fund['source_id']-1]
            source_code = find_code_by_isin(fund['isin'], source['name'], source['search_url'])
            print(fund['isin'], source_code)               # TODO: remove
            if source_code != 'UNSET':
                cur_ffo.execute(update_ffo, (source_code, fund['id'], fund['source_id']))
            # Commit the changes
            cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    print("updated funds list:", fund_list)                # TODO: remove

    # PART III - Update financial info in tables "fin_info" and "fund"
    # ----------------------------------------------------------------
    cur_ffo = cnx.cursor(buffered=True)         # TODO: is cursor change necessary?
    update_ffo = (
        " UPDATE fin_info AS ffo"
        " SET name = %s, rating = %s, benchmark = %s, lvdate = DATE(%s), lvalue = %s, currency_id = %s,"
        "     date_ytd = DATE(%s), perf_a = %s, perf_am1 = %s, perf_am2 = %s, perf_am3 = %s"
        " WHERE ffo.fund_id = %s AND ffo.source_id = %s")
    cur_fnd = cnx.cursor(buffered=True)
    update_fnd = (
        " UPDATE fund AS fnd"
        " SET last_lvalue = %s"
        " WHERE fnd.id = %s")
    # Iterate through the funds to update
    for fund in fund_list:
        print('fund:', fund)
        if fund['code'] != 'UNSET':
            # Retrieve full info for fund with specified source code (i.e. not 'UNSET')
            # calling get_info(source.id, source.fund.url, fin_info.code)
            source = source_list[fund['source_id'] - 1]
            print("calling get_info(", fund['source_id'], ",", source['fund_url'], ",", fund['code'], ")")
            info = get_info(fund['source_id'], source['fund_url'], fund['code'])
            print(info)
            if len(info) > 1:
                # converting date formats from DD/MM/YYYY to YYYYY-MM-DD
                info['lvdate'] = datetime.datetime.strptime(info['lvdate'], "%d/%m/%Y").strftime("%Y-%m-%d")
                info['date_ytd'] = datetime.datetime.strptime(info['date_ytd'], "%d/%m/%Y").strftime("%Y-%m-%d")
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
                cur_ffo.execute(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'],
                                currency_id, info['date_ytd'], info['perf_a'], info['perf_am1'],
                                info['perf_am2'], info['perf_am3'], fund['id'], fund['source_id']))

                # update fund table with last-lvalue (converted in euros)
                lvalue = info['lvalue'] / currency_value
                print(update_fnd, (lvalue, fund['id']))
                cur_fnd.execute(update_fnd, (lvalue, fund['id']))

                # Commit the changes
                cnx.commit()

                # Update financial info in table "fund_hist"
                # TODO: get info from Morningstar specific API and update database with new known values
                cnx = mysql.connector.connect(**db_config)
                cur_ffo = cnx.cursor(buffered=True)
                insert_hist_values = (
                    "INSERT INTO fund_hist (fund_id, lvdate, lvalue) "
                    "VALUES (%s, %s, %s)")
                if source['name'] == 'morningstar':
                    starts = "1991-12-31"
                    today = datetime.date.today()
                    ends = (today.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m-%j")
                    ms_code = info['code']
                    historical_values = get_historical_values(ms_code, "EUR", "monthly", starts, ends)
                    if len(historical_values) > 0:
                        for i in range(len(historical_values)):
                            ts = historical_values[i][0]/1000         # timestamp given in milliseconds
                            lvdate = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
                            lvalue = historical_values[i][1]
                            print(insert_hist_values, (fund['id'], lvdate, lvalue))
                            cur_fnd.execute(insert_hist_values, (fund['id'], lvdate, lvalue))
                            # Commit the changes
                            cnx.commit()


# Retrieve list of funds to be updated
# Array of dictionary: (id, isin, fin_id, source_id, code)
def get_fund_list():
    cnx = mysql.connector.connect(**db_config)
    # Get two buffered cursors
    cursor = cnx.cursor(buffered=True, dictionary=True)
    query = (
        "SELECT fnd.id, fnd.isin, ffo.id AS 'fin_id', ffo.source_id, ffo.code "
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
# Array of dictionary: (id, name, search_url, fund_url)
def get_source_list():
    cnx = mysql.connector.connect(**db_config)
    cur_src = cnx.cursor(buffered=True, dictionary=True)
    query_src = "SELECT * FROM source"
    cur_src.execute(query_src)
    source_list = []
    for row in cur_src:
        source_list.append(row)
    cur_src.close()
    cnx.close()
    return source_list


# Retrieve list of currencies
# Array of dictionary: (id, name, search_url, fund_url)
def get_currency_list():
    cnx = mysql.connector.connect(**db_config)
    cur_cur = cnx.cursor(buffered=True, dictionary=True)
    query_cur = "SELECT * FROM currency"
    cur_cur.execute(query_cur)
    currency_list = []
    for row in cur_cur:
        currency_list.append(row)
    cur_cur.close()
    cnx.close()
    return currency_list


# Retrieve fund source code by ISIN
def find_code_by_isin(isin, name, search_url):
    """
    Search for an asset's Morningstar/Quantalys ID given its exact ISIN
    :param isin:
    :param name: name of source
    :param search_url:
    :return: source internal code associated with isin or False
    """
    # default value if an error occurred while requesting page
    code = 'UNSET'
    target = search_url + isin
    timeout = 10
    soup = get_soup(target, timeout)
    if soup:
        if name == "morningstar":
            if soup.find("td", "searchLink"):
                code = soup.find("td", "searchLink").children.__next__().get('href')[-10:]
        else:
            if soup.find('input', id='id-produit'):
                code = soup.find('input', id='id-produit')['value']
    return code


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import datetime

import mysql.connector
from config import db_config
from scraping import get_soup
from sfibot import get_info


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
        " SET name = %s, rating = %s, benchmark = %s, lvdate = DATE(%s), lvalue = %s, currency = %s,"
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
                info['lvalue'] = str(info['lvalue']).replace(',', '.')
                info['perf_a'] = str(info['perf_a']).replace(',', '.')
                info['perf_am1'] = str(info['perf_am1']).replace(',', '.')
                info['perf_am2'] = str(info['perf_am2']).replace(',', '.')
                info['perf_am3'] = str(info['perf_am3']).replace(',', '.')
                # update fund info in fin_info and fund tables
                print("updating", info['code'])           # TODO: remove
                print(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'],
                                   info['currency'], info['date_ytd'], info['perf_a'], info['perf_am1'],
                                   info['perf_am2'], info['perf_am3'], fund['id'], fund['source_id']))
                cur_ffo.execute(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'],
                                info['currency'], info['date_ytd'], info['perf_a'], info['perf_am1'],
                                info['perf_am2'], info['perf_am3'], fund['id'], fund['source_id']))
                print(update_fnd, (info['lvalue'], fund['id']))
                cur_fnd.execute(update_fnd, (info['lvalue'], fund['id']))
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

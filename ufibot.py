# -*- coding: utf-8 -*-

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
    # Iterate through the funds to update list
    for fund in fund_list:
        # get missing source codes
        source_code = find_id_by_isin(fund[1])
        # insert new funds for all sources
        for source in source_list:
            # select funds no fin_info.id found
            if not fund[2]:
                # get source internal code
                s_code = source_code[source_list[source[0]-1][1]]
                cur_ffo.execute(insert_new_funds, (fund[0], source[0], fund[1], s_code))
        # Commit the changes
        cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    print("updated funds list:", fund_list)                # TODO: remove

    # PART II - Update financial info in tables "fin_info" and "fund"
    # ---------------------------------------------------------------
    cur_ffo = cnx.cursor(buffered=True)         # TODO: is cursor change necessary?
    update_ffo = (
        " UPDATE fin_info AS ffo"
        " SET name = %s, rating = %s, benchmark = %s, lvdate =%s, lvalue = %s, currency = %s,"
        "     date_ytd = %s, perf_a = %s, perf_am1 = %s, perf_am2 = %s, perf_am3 = %s"
        " WHERE ffo.fund_id = %s AND ffo.source_id = %s")
    cur_fnd = cnx.cursor(buffered=True)
    update_fnd = (
        " UPDATE fund AS fnd"
        " SET last_lvalue = %s"
        " WHERE fnd.id = %s")
    # Iterate through the funds to update list
    for fund in fund_list:
        print('fund:', fund)
        if fund[4] != 'UNSET':
            # Retrieve full info for fund with specified source code (i.e. not 'UNSET')
            # calling get_info(source.id, source.fund.url, fin_info.code)
            s_url = source_list[fund[3] - 1][3]
            print("calling get_info(", fund[3], ",", s_url, ",", fund[4], ")")
            info = get_info(fund[3], s_url, fund[4])
            print(info)
            # update fund info in fin_info and fund tables
            print("updating", info['code'])           # TODO: remove
            # cur_ffo.execute(update_ffo, (info[5], info[6], info[7], info[8], info[9],
            print(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'], info['currency'],
                               info['date_ytd'], info['perf_a'], info['perf_am1'], info['perf_am2'], info['perf_am3'],
                               fund[0], fund[3]))
            print(update_fnd, (info['lvalue'], fund[0]))
            # cur_fnd.execute(update_fnd, (info[9], info[1]))
            # Commit the changes
            cnx.commit()


# Retrieve list of funds to be updated
# Array of tuples: (fund ID, fund ISIN, fin ID, fin source, fin CODE)
def get_fund_list():
    cnx = mysql.connector.connect(**db_config)
    # Get two buffered cursors
    cursor = cnx.cursor(buffered=True)
    query = (
        "SELECT fnd.id, fnd.isin, ffo.id, ffo.source_id, ffo.code "
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
        timeout = 10
        soup = get_soup(target, timeout)
        # default value if an error occurred while requesting page
        code[name] = 'UNSET'
        if soup:
            if name == "morningstar":
                if soup.find("td", "searchLink"):
                    code[name] = soup.find("td", "searchLink").children.__next__().get('href')[-10:]
            else:
                if soup.find('input', id='id-produit'):
                    code[name] = soup.find('input', id='id-produit')['value']
    cursor.close()
    cnx.close()
    return code


if __name__ == '__main__':
    main()

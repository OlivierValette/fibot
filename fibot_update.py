# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import mysql.connector
from config import db_config
from scraping import get_soup
from fibot_search import get_info
from fibot_api import get_historical_values


# Main function
# fibot: update financial data in "fin_info" by scraping sites in "source"
def main():

    # Open log file
    when = datetime.now()
    logname = './log/fibot_u_' + when.strftime("%Y%m%d.%H%M%S") + '.log'
    log = open(logname, "w+")
    log.write('\nfibot (update) on ' + when.strftime("%Y-%m-%d %H:%M:%S"))
    # Get list of funds to update (only active funds in "funds")
    fund_list = get_fund_list()
    log.write('\nfund list:\n')
    log.write('\n'.join(map(str, fund_list)))
    # Get list of sources
    source_list = get_source_list()
    log.write('\nsource list:\n')
    log.write('\n'.join(map(str, source_list)))

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
    log.write('\nupdated funds list:\n')
    log.write('\n'.join(map(str, fund_list)))

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
        if fund['code'] == 'UNSET':   # to temporary skips this part  SKIP<->UNSET
            # new attempt to get source internal code
            source = source_list[fund['source_id']-1]
            source_code = find_code_by_isin(fund['isin'], source['name'], source['search_url'])
            log.write("\nsource code for ISIN: " + fund['isin'] + ' ID:' + source_code)
            if source_code != 'UNSET':
                cur_ffo.execute(update_ffo, (source_code, fund['id'], fund['source_id']))
            # Commit the changes
            cnx.commit()

    # Get updated list of funds to update
    fund_list = get_fund_list()
    log.write('\nupdated funds list:\n')
    log.write('\n'.join(map(str, fund_list)))

    # PART III - Update financial info in tables "fin_info" and "fund"
    # ----------------------------------------------------------------
    # Iterate through the funds to update
    for fund in fund_list:
        cur_ffo = cnx.cursor(buffered=True)
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
        print('fund: ' + str(fund))
        log.write('\n----------\n----------fund: ' + str(fund))
        if fund['code'] != 'UNSET':
            # Retrieve full info for fund with specified source code (i.e. not 'UNSET')
            # calling get_info(source.id, source.fund.url, fin_info.code)
            source = source_list[fund['source_id'] - 1]
            log.write('\ncalling get_info(' + str(fund['source_id']) + ", " + source['fund_url'] + ", " + fund['code'] + ")")
            log.close()
            info = get_info(fund['source_id'], source['fund_url'], fund['code'], logname)
            log = open(logname, "a+")
            log.write('\n\n----------output:' + str(info))
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
                log.write('\ncurrency list:\n')
                log.write(', '.join(map(str, currency_list)))
                currency_id = False
                currency_value = 1.
                for currency in currency_list:
                    if currency['code'] == info['currency']:
                        currency_id = currency['id']
                        currency_value = currency['value']
                log.write('\nselected currency: ' + str(currency_id) + ' (' + info['currency'] +
                          ') - Taux: {:.2f}'.format(currency_value))
                if not currency_id:
                    currency_id = 1     # if not in currency, default set to EUR, TODO: improve

                # update fund info in fin_info
                log.write('\nupdating ' + info['code'])
                log.write(update_ffo + ' (' + info['name'] + ', ' + info['rating'] + ', ' + info['benchmark'] + ', ' +
                          info['lvdate'] + ', ' + '{:.2f}'.format(info['lvalue']) + ', ' + str(currency_id) + ', ' +
                          info['date_ytd'] + ', ' + '{:.2f}'.format(info['perf_a']) + ', ' +
                          '{:.2f}'.format(info['perf_am1']) + ', ' + '{:.2f}'.format(info['perf_am2']) + ', ' +
                          '{:.2f}'.format(info['perf_am3']) + ', ' + str(fund['id']) + ', ' + str(fund['source_id']) + ')')
                cur_ffo.execute(update_ffo, (info['name'], info['rating'], info['benchmark'], info['lvdate'], info['lvalue'],
                                currency_id, info['date_ytd'], info['perf_a'], info['perf_am1'],
                                info['perf_am2'], info['perf_am3'], fund['id'], fund['source_id']))

                # update fund table with last-lvalue (converted in euros)
                lvalue = info['lvalue'] / currency_value
                log.write('\n' + update_fnd + ' (' + '{:.2f}'.format(lvalue) + ', ' + str(fund['id']) + ')')
                cur_fnd.execute(update_fnd, (lvalue, fund['id']))

                # Commit the changes
                cnx.commit()

                # Update financial info in table "fund_hist"
                # Get info from Morningstar specific API and update database with new known values
                cur_fdh = cnx.cursor(buffered=True, dictionary=True)
                query_hist_values = (
                    " SELECT MAX(lvdate) AS ldate"
                    " FROM fund_hist"
                    " WHERE fund_id = %s")
                insert_hist_values = (
                    "INSERT INTO fund_hist (fund_id, lvalue, lvdate) "
                    "VALUES (%s, %s, %s)")
                if source['name'] == 'morningstar':
                    # find last date already stored in database
                    ms_code = info['code']
                    cur_fdh.execute(query_hist_values, (fund['id'],))
                    for row in cur_fdh:
                        ldate = row['ldate']
                    if not ldate: ldate = datetime(1991, 1, 1)
                    cur_fdh.close()
                    log.write('\nLast date retrieved: ' + ldate.strftime("%Y-%m-%d"))
                    if ldate.month == 12:
                        starts = ldate.replace(year=ldate.year + 1, month=1, day=1).strftime("%Y-%m-%d")
                    else:
                        starts = ldate.replace(month=ldate.month + 1, day=1).strftime("%Y-%m-%d")
                    today = datetime.today()
                    ends = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
                    log.write('\nstarts:' + starts + ' - ends:' + ends)
                    if starts < ends:
                        historical_values = get_historical_values(ms_code, "EUR", "monthly", starts, ends)
                        if len(historical_values) > 0:
                            cur_fdh = cnx.cursor(buffered=True)
                            log.write('\ninsert: ')
                            for i in range(len(historical_values)):
                                ts = historical_values[i][0]/1000         # timestamp given in milliseconds
                                lvdate = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
                                lvalue = historical_values[i][1]
                                log.write('(' + str(fund['id']) + ', ' + '{:.2f}'.format(lvalue) + ', ' + lvdate + ')')
                                cur_fdh.execute(insert_hist_values, (fund['id'], lvalue, lvdate))
                                # Commit the changes
                                cnx.commit()
    # closing log file
    log.close()


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
    timeout = 10
    soup = get_soup(search_url, isin, timeout)
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

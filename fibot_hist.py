# -*- coding: utf-8 -*-

import mysql.connector
from config import db_config


# Main function
# fibot: update historical tables with last recorded values
def main():
    cnx = mysql.connector.connect(**db_config)
    cur_fdh = cnx.cursor(buffered=True, dictionary=True)
    query_hist_values = (
        " SELECT MAX(lvdate)"
        " AS ldate"
        " FROM portfolio_hist"
        " WHERE fund_id = %s")
    insert_hist_values = (
        "INSERT INTO fund_hist (fund_id, lvalue, lvdate) "
        "VALUES (%s, %s, %s)")


if __name__ == '__main__':
    main()

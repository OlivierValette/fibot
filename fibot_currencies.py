# -*- coding: utf-8 -*-

import mysql.connector
from config import db_config
from fibot_api import get_currencies
from datetime import datetime


# Main function
# fibot_currencies: update currencies in currency table
def main():
    cnx = mysql.connector.connect(**db_config)
    cur_cur = cnx.cursor(buffered=True)
    update_cur = (
        " UPDATE currency AS c"
        " SET value = %s WHERE c.code = %s"
    )

    # Log file
    when = datetime.now()
    log = open('./log/fibot_c.log', "a+")
    log.write('\nfibot currencies (on ' + when.strftime("%Y-%m-%d %H:%M:%S") + '): ')

    # getting currencies from API
    currencies = get_currencies()
    log.write(str(currencies))
    for currency in currencies['rates']:
        cur_cur.execute(update_cur, (currencies['rates'][currency], currency))

    cnx.commit()


if __name__ == '__main__':
    main()

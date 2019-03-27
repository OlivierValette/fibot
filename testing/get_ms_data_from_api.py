# MS API for historical values
# monthly update
import json
import requests
from datetime import datetime


def get_historical_values(id, cur, freq, d1, d2) :
    api_token = ''
    API_URL_BASE = "http://tools.morningstar.fr/api/rest.svc/timeseries_price/ok91jeenoo?"
    P_ID = "id="
    P_CUR = "&currencyId="
    P_TYPE = "&idtype=Morningstar"
    P_PRICE = "&priceType="
    P_FREQ = "&frequency="
    P_FROM = "&startDate="
    P_TO = "&endDate="
    P_FORMAT= "&outputType=COMPACTJSON"

    api_url = API_URL_BASE + P_ID + id + P_CUR + cur + P_TYPE + P_PRICE + P_FREQ + freq + P_FROM + d1 + P_TO + d2 + P_FORMAT
    headers = {'Content-Type': 'application/json'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


ms_id = "F0GBR04QCM"
cur_id = "EUR"
frequency = "monthly"
starts = "1991-12-31"
ends = "2018-12-31"
historical_values = get_historical_values(ms_id, cur_id, frequency, starts, ends)

if len(historical_values) > 0:
    print("Historical data for : " + ms_id)
    for i in range(len(historical_values)-1):
        # timestamp given in milliseconds
        ts = historical_values[i][0]/1000
        print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'), " -> ", historical_values[i][1], cur_id)
else:
    print('[!] Request Failed')

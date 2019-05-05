# MS API for historical values
# monthly update
import json
import requests
from datetime import datetime


def get_historical_values(fid, cur, freq, d1, d2):
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

    api_url = API_URL_BASE + P_ID + fid + P_CUR + cur + P_TYPE + P_PRICE + P_FREQ + freq + P_FROM + d1 + P_TO + d2 + P_FORMAT
    headers = {'Content-Type': 'application/json'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

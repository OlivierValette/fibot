# fibot - financial robot
**fibot** is a python scrapper used to get information on mutual funds for *www.fundlog.fr*, a portfolio management app.
Values are saved to *fundlog* database

Database also contains financial source website urls, in `source` table

## Connecting to financial information websites

### Scraping
Function `find_code_by_isin()` is used to get internal source id

Scraping parameters are defined in the `scraping` table

### APIs
File `fibot_api.py`
with two functions:

- `get_historical_values()` for Morningstar historical values
- `get_currencies()` for Openrates currencies

## Updating funds
File `fibot_update.py`

update financial data in "fin_info" by scraping sites in "source"

## Updating funds historical values
File `fibot_hist.py`

update historical tables fund_hist
 
## Install
### environment
Create a fibot folder and an environment 'fibot'
```bash
python3 -m venv fibot_env
source fibot_env/bin/activate
```
### database
Set database parameters in file `config.py`

### cron
#### daily
`fibot_currencies.py`

`fibot_update.py`

#### monthly
`fibot_hist.py`

TODO: log cleaning
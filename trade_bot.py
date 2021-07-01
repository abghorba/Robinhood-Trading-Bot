import robin_stocks.robinhood as robinhood
import pandas as pd

import os
import time

robin_user = os.environ.get("robinhood_username")
robin_pass = os.environ.get("robinhood_password")

robinhood.login(username=robin_user,
         password=robin_pass,
         expiresIn=86400,
         by_sms=True)


symbol = 'ETH'

eth_info = robinhood.crypto.get_crypto_quote(symbol)
print(eth_info)

eth_history = robinhood.crypto.get_crypto_historicals(symbol, interval='hour',span='week', bounds='24_7', info=None)
print(eth_history)

robinhood.logout()
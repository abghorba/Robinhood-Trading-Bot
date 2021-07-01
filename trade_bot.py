import robin_stocks.robinhood as robinhood
import pandas as pd

import os
import time

class TradeBot():
    def __init__(self, trade_list):
        self.trade_list = trade_list
    
    def is_time_to_buy(self, crypto_symbol):
        """
        Determines if we are to buy and returns a bool.
        """
        return True

    def is_time_to_sell(self, crypto_symbol):
        """
        Determines if we are to sell and returns a bool.
        """
        return False

    def trade(self):
        """
        Places buy/sell orders for fractional shares of stock.
        """
        for ticker_symbol in self.trade_list:
            amount_in_dollars = 1
            if self.is_time_to_buy(ticker_symbol):
                print(f"Buying ${amount_in_dollars} of {ticker_symbol}...")
                robinhood.orders.order_buy_fractional_by_price(ticker_symbol, 
                                                                amount_in_dollars, 
                                                                timeInForce='gfd', 
                                                                extendedHours=False,
                                                                jsonify=True)
                print(f"Successfully bought ${amount_in_dollars} of {ticker_symbol}.")
            else:
                print(f"It is not time to buy {ticker_symbol}.")
            
            if self.is_time_to_sell(ticker_symbol):
                print(f"Selling ${amount_in_dollars} of {ticker_symbol}...")
                robinhood.orders.order_sell_fractional_by_price(ticker_symbol, 
                                                                amount_in_dollars, 
                                                                timeInForce='gfd', 
                                                                extendedHours=False,
                                                                jsonify=True)
                print(f"Successfully sold ${amount_in_dollars} of {ticker_symbol}.")
            else:
                print(f"It is not time to sell {ticker_symbol}.")          

class TradeBotCrypto(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)
        crypto_list = robinhood.crypto.get_crypto_currency_pairs(info='asset_currency')
        self.tradeable_cryptos = set()
        for crypto in crypto_list:
            self.tradeable_cryptos.add(crypto['code'])

    def trade(self):
        """
        Places buy/sell orders for cryptocurrency.
        """
        for crypto_symbol in self.trade_list:
            if crypto_symbol in self.tradeable_cryptos:
                amount_in_dollars = 1
                if self.is_time_to_buy(crypto_symbol):
                    print(f"Buying ${amount_in_dollars} of {crypto_symbol}...")
                    robinhood.orders.order_buy_crypto_by_price(crypto_symbol, 
                                                            amount_in_dollars, 
                                                            timeInForce='gfd', 
                                                            jsonify=True)
                    print(f"Successfully bought ${amount_in_dollars} of {crypto_symbol}.")
                else:
                    print(f"It is not time to buy {crypto_symbol}.")
                
                if self.is_time_to_sell(crypto_symbol):
                    print(f"Selling ${amount_in_dollars} of {crypto_symbol}...")
                    robinhood.orders.order_sell_crypto_by_price(crypto_symbol, 
                                                                amount_in_dollars, 
                                                                timeInForce='gfd', 
                                                                jsonify=True)
                    print(f"Successfully sold ${amount_in_dollars} of {crypto_symbol}.")
                else:
                    print(f"It is not time to sell {crypto_symbol}.")
            else:
                print(f"Cryptocurrency {crypto_symbol} is not supported by Robinhood.")  

def main():
    robin_user = os.environ.get("robinhood_username")
    robin_pass = os.environ.get("robinhood_password")

    robinhood.login(username=robin_user,
            password=robin_pass,
            expiresIn=86400,
            by_sms=True)

    """
    Returns a dictionary where the keys are the stock tickers and 
    the value is another dictionary that has the stock price, 
    quantity held, equity, percent change, equity change, type, 
    name, id, pe ratio, percentage of portfolio, and average buy price.
    """
    # current_holdings = robinhood.build_holdings()
    # print(current_holdings)

    stock_trade_list = ['AMZN', 'AAPL', 'MSFT']
    trade_bot = TradeBot(stock_trade_list)
    # trade_bot.trade()

    crypto_trade_list = ['DOGE']
    crypto_bot = TradeBotCrypto(crypto_trade_list)
    #crypto_bot.trade()
    
    current_holdings = robinhood.build_holdings()
    print(current_holdings)


if __name__ == "__main__":
    main()
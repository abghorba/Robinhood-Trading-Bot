import robin_stocks.robinhood as robinhood
import pandas as pd

import time

class TradeBot():
    def __init__(self, trade_list):
        self.trade_list = trade_list
    
    def update_trade_list(self, new_trade_list):
        self.trade_list = new_trade_list

    def get_current_trade_list(self):
        return self.trade_list

    def make_order_recommendation(self, ticker_symbol):
        """
        Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.
        Returns 'b' for buy, 's' for sell, or None for neither.
        """
        stock_history = robinhood.stocks.get_stock_historicals(ticker_symbol, 
                                                               interval='day', 
                                                               span='year' )
        stock_history_df = pd.DataFrame(stock_history)
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')

        #Calculate the 200-day moving average.
        stock_200_day_history = stock_history_df.tail(200)
        moving_average_200_day = stock_200_day_history['close_price'].mean()
        print(moving_average_200_day)

        #Calculate the 50-day moving average.
        stock_50_day_history = stock_history_df.tail(50)
        moving_average_50_day = stock_50_day_history['close_price'].mean()
        print(moving_average_50_day)

        if moving_average_50_day > moving_average_200_day:
            return 'b'
        elif moving_average_50_day < moving_average_200_day:
            return 's'
        else:
            return None

    def trade(self, amount_in_dollars = 1):
        """
        Places buy/sell orders for fractional shares of stock.
        """
        for ticker_symbol in self.trade_list:
            action = self.make_order_recommendation(ticker_symbol)

            if action == 'b':
                print(f"Buying ${amount_in_dollars} of {ticker_symbol}...")
                robinhood.orders.order_buy_fractional_by_price(ticker_symbol, 
                                                                amount_in_dollars, 
                                                                timeInForce='gfd', 
                                                                extendedHours=False,
                                                                jsonify=True)
                print(f"Successfully bought ${amount_in_dollars} of {ticker_symbol}.")
            else:
                print(f"It is not time to buy {ticker_symbol}.")
            
            if action == 's':
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

    def make_order_recommendation(self, crypto_symbol):
        """
        Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.
        Returns 'b' for buy, 's' for sell, or None for neither.
        """
        if crypto_symbol not in self.tradeable_cryptos:
            return None

        crypto_history = robinhood.crypto.get_crypto_historicals(crypto_symbol, 
                                                                 interval='day', 
                                                                 span='year' )
        crypto_history_df = pd.DataFrame(crypto_history)
        crypto_history_df['close_price'] = pd.to_numeric(crypto_history_df['close_price'], errors='coerce')

        #Calculate the 200-day moving average.
        crypto_200_day_history = crypto_history_df.tail(200)
        moving_average_200_day = crypto_200_day_history['close_price'].mean()
        print(moving_average_200_day)

        #Calculate the 50-day moving average.
        crypto_50_day_history = crypto_history_df.tail(50)
        moving_average_50_day = crypto_50_day_history['close_price'].mean()
        print(moving_average_50_day)

        if moving_average_50_day > moving_average_200_day:
            return 'b'
        elif moving_average_50_day < moving_average_200_day:
            return 's'
        else:
            return None

    def trade(self, amount_in_dollars = 1):
        """
        Places buy/sell orders for cryptocurrency.
        """
        for crypto_symbol in self.trade_list:
            if crypto_symbol in self.tradeable_cryptos:
                action = self.make_order_recommendation(crypto_symbol)

                if action == 'b':
                    print(f"Buying ${amount_in_dollars} of {crypto_symbol}...")
                    robinhood.orders.order_buy_crypto_by_price(crypto_symbol, 
                                                               amount_in_dollars, 
                                                               timeInForce='gfd', 
                                                               jsonify=True)
                    print(f"Successfully bought ${amount_in_dollars} of {crypto_symbol}.")
                else:
                    print(f"It is not time to buy {crypto_symbol}.")
                
                if action == 's':
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

class TradeBotVWAP(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def make_order_recommendation(self, ticker_symbol, buy_threshold=0, sell_threshold=0):
        """
        Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.
        Returns 'b' for buy, 's' for sell, or None for neither.
        """
        stock_history = robinhood.stocks.get_stock_historicals(ticker_symbol, 
                                                               interval='5minute', 
                                                               span='day' )
        stock_history_df = pd.DataFrame(stock_history)
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')
        stock_history_df['volume'] = pd.to_numeric(stock_history_df['volume'], errors='coerce')

        #Calculate the VWAP from the last day in 5 minute intervals.
        sum_of_volumes = stock_history_df['volume'].sum()
        sum_of_prices_times_volumes = stock_history_df['volume'].dot(stock_history_df['close_price'])
        vwap = round(sum_of_prices_times_volumes / sum_of_volumes, 2)
        print(f"vwap is {vwap}")

        #Get the current market price of the stock.
        current_price = float(robinhood.stocks.get_latest_price(ticker_symbol, includeExtendedHours=False)[0])
        print(f"current price is {current_price}")

        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return None

class TradeBotCryptoVWAP(TradeBotCrypto):
    def __init__(self, trade_list):
        TradeBotCrypto.__init__(self, trade_list)

    def make_order_recommendation(self, crypto_symbol, buy_threshold=0, sell_threshold=0):
        """
        Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.
        Returns 'b' for buy, 's' for sell, or None for neither.
        """
        crypto_history = robinhood.crypto.get_crypto_historicals(crypto_symbol, 
                                                                 interval='5minute', 
                                                                 span='day')
        crypto_history_df = pd.DataFrame(crypto_history)
        crypto_history_df['close_price'] = pd.to_numeric(crypto_history_df['close_price'], errors='coerce')
        crypto_history_df['volume'] = pd.to_numeric(crypto_history_df['volume'], errors='coerce')
        print(crypto_history_df)

        #Calculate the VWAP from the last day in 5 minute intervals.
        #Note: there is a bug that returns 0 in the volume columns!
        #This breaks this algorithm, and is pending fix.
        sum_of_volumes = crypto_history_df['volume'].sum()
        sum_of_prices_times_volumes = crypto_history_df['volume'].dot(crypto_history_df['close_price'])
        print(sum_of_prices_times_volumes)
        print(sum_of_volumes)
        vwap = sum_of_prices_times_volumes / sum_of_volumes
        print(f"vwap is {vwap}")

        #Get the current market price of the stock.
        current_price = robinhood.crypto.get_crypto_quote(crypto_symbol)['ask_price']
        print(f"current price is {current_price}")

        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return None

class TradeBotPairsTrading(TradeBot):
    pass

class TradeBotCryptoPairsTrading(TradeBotCrypto):
    pass

class TradeBotSentimentAnalysis(TradeBot):
    pass

class TradeBotCryptoSentimentAnalysis(TradeBotCrypto):
    pass



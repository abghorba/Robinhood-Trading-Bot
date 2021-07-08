import robin_stocks.robinhood as robinhood
import pandas as pd

import time

class TradeBot():
    def __init__(self, trade_list=[]):
        """
        Constructs the TradeBot object with the trade list.

        :param trade_list: A list of ticker symbols.
        :type trade_list: list
        :returns: None

        """
        self.trade_list = trade_list
    
    def update_trade_list(self, new_trade_list):
        """
        Updates the current trade list.

        :param new_trade_list: The list of ticker symbols to update to.
        :type new_trade_list: list
        :returns: None

        """
        self.trade_list = new_trade_list

    def get_current_trade_list(self):
        """
        Returns the current trade list.

        :returns: The current trade list as a list.

        """

        return self.trade_list

    def make_order_recommendation(self, symbol):
        """
        Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.
        Returns 'b' for buy, 's' for sell, or 'x' for neither.

        :param symbol: A ticker symbol.
        :type symbol: str
        :returns: A string with the order recommendation.

        """
        stock_history = robinhood.stocks.get_stock_historicals(symbol, 
                                                               interval='day', 
                                                               span='year' )
        stock_history_df = pd.DataFrame(stock_history)
        print(stock_history_df)
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')

        #Calculate the 200-day moving average.
        stock_200_day_history = stock_history_df.tail(200)
        moving_average_200_day = stock_200_day_history['close_price'].mean()

        #Calculate the 50-day moving average.
        stock_50_day_history = stock_history_df.tail(50)
        moving_average_50_day = stock_50_day_history['close_price'].mean()

        if moving_average_50_day > moving_average_200_day:
            return 'b'
        elif moving_average_50_day < moving_average_200_day:
            return 's'
        else:
            return 'x'

    def has_sufficient_funds_available(self, amount_in_dollars):
        """
        Returns a boolean if user's account has enough buying power
        to execute a buy order.

        :param amount_in_dollars: The amount to transact with.
        :type amount_in_dollars: float
        :returns: bool

        """
        available_funds = float(robinhood.profiles.load_account_profile(info="buying_power"))

        return available_funds >= amount_in_dollars

    def has_sufficient_equity(self, symbol, amount_in_dollars):
        """
        Returns a boolean if user's account has enough equity in
        the given position to execute a sell order. If the user
        does not own the position, returns a False.

        :param symbol: A ticker symbol.
        :param amount_in_dollars: The amount to transact with.
        :type amount_in_dollars: float
        :type symbol: str
        :returns: bool

        """
        current_holdings = robinhood.build_holdings()
        if symbol in current_holdings:
            current_position = current_holdings[symbol]
            current_equity_in_position = float(current_position['equity'])
            return current_equity_in_position >= amount_in_dollars
        else:
            return False

    def trade(self, amount_in_dollars = 1):
        """
        Places buy/sell orders for fractional shares of stock.

        :param amount_in_dollars: The amount to transact with.
        :type amount_in_dollars: float
        :returns: None

        """
        for symbol in self.trade_list:
            action = self.make_order_recommendation(symbol)

            if action == 'b':
                if self.has_sufficient_funds_available(amount_in_dollars):
                    print(f"Buying ${amount_in_dollars} of {symbol}...")
                    robinhood.orders.order_buy_fractional_by_price(symbol, 
                                                                   amount_in_dollars, 
                                                                   timeInForce='gfd', 
                                                                   extendedHours=False,
                                                                   jsonify=True)
                    print(f"Successfully bought ${amount_in_dollars} of {symbol}.")
                else:
                    print("Sufficient funds are not available for this purchase.") 
            elif action == 's':
                if self.has_sufficient_equity(symbol, amount_in_dollars):
                    print(f"Selling ${amount_in_dollars} of {symbol}...")
                    robinhood.orders.order_sell_fractional_by_price(symbol, 
                                                                    amount_in_dollars, 
                                                                    timeInForce='gfd', 
                                                                    extendedHours=False,
                                                                    jsonify=True)
                    print(f"Successfully sold ${amount_in_dollars} of {symbol}.")
                else:
                    print(f"Sufficient equity is not available for this sale.")
            else:
                print("Conditions are not met for either a purchase or a sale.")         

class TradeBotCrypto(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)
        crypto_list = robinhood.crypto.get_crypto_currency_pairs(info='asset_currency')
        self.tradeable_cryptos = set()
        for crypto in crypto_list:
            self.tradeable_cryptos.add(crypto['code'])

    def make_order_recommendation(self, symbol):
        """
        Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.
        Returns 'b' for buy, 's' for sell, or None for neither.
        """
        if symbol not in self.tradeable_cryptos:
            return None

        crypto_history = robinhood.crypto.get_crypto_historicals(symbol, 
                                                                 interval='day', 
                                                                 span='year' )
        crypto_history_df = pd.DataFrame(crypto_history)
        crypto_history_df['close_price'] = pd.to_numeric(crypto_history_df['close_price'], errors='coerce')

        #Calculate the 200-day moving average.
        crypto_200_day_history = crypto_history_df.tail(200)
        moving_average_200_day = crypto_200_day_history['close_price'].mean()

        #Calculate the 50-day moving average.
        crypto_50_day_history = crypto_history_df.tail(50)
        moving_average_50_day = crypto_50_day_history['close_price'].mean()

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
        for symbol in self.trade_list:
            if symbol in self.tradeable_cryptos:
                action = self.make_order_recommendation(symbol)

                if action == 'b':
                    print(f"Buying ${amount_in_dollars} of {symbol}...")
                    robinhood.orders.order_buy_crypto_by_price(symbol, 
                                                               amount_in_dollars, 
                                                               timeInForce='gfd', 
                                                               jsonify=True)
                    print(f"Successfully bought ${amount_in_dollars} of {symbol}.")
                else:
                    print(f"It is not time to buy {symbol}.")
                
                if action == 's':
                    print(f"Selling ${amount_in_dollars} of {symbol}...")
                    robinhood.orders.order_sell_crypto_by_price(symbol, 
                                                                amount_in_dollars, 
                                                                timeInForce='gfd', 
                                                                jsonify=True)
                    print(f"Successfully sold ${amount_in_dollars} of {symbol}.")
                else:
                    print(f"It is not time to sell {symbol}.")
            else:
                print(f"Cryptocurrency {symbol} is not supported by Robinhood.")  

class TradeBotVWAP(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def make_order_recommendation(self, symbol, buy_threshold=0, sell_threshold=0):
        """
        Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.
        Returns 'b' for buy, 's' for sell, or 'x' for neither.

        :param symbol: A ticker symbol.
        :type symbol: str
        :returns: A string with the order recommendation.

        """
        stock_history = robinhood.stocks.get_stock_historicals(symbol, 
                                                               interval='5minute', 
                                                               span='day' )
        stock_history_df = pd.DataFrame(stock_history)
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')
        stock_history_df['volume'] = pd.to_numeric(stock_history_df['volume'], errors='coerce')

        #Calculate the VWAP from the last day in 5 minute intervals.
        sum_of_volumes = stock_history_df['volume'].sum()
        sum_of_prices_times_volumes = stock_history_df['volume'].dot(stock_history_df['close_price'])
        vwap = round(sum_of_prices_times_volumes / sum_of_volumes, 2)

        #Get the current market price of the stock.
        current_price = float(robinhood.stocks.get_latest_price(symbol, includeExtendedHours=False)[0])

        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return 'x'

# There is a bug in the robin_stocks library that breaks
# this bot. DO NOT USE.
class TradeBotCryptoVWAP(TradeBotCrypto):
    def __init__(self, trade_list):
        TradeBotCrypto.__init__(self, trade_list)

    def make_order_recommendation(self, symbol, buy_threshold=0.00, sell_threshold=0.00):
        """
        Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.
        Returns 'b' for buy, 's' for sell, or None for neither.

        :param symbol: A ticker symbol.
        :param buy_threshold: The amount amove the VWAP you would still like to buy.
        :param sell_threshold: The amount amove the VWAP you would still like to sell.
        :type symbol: str
        :type buy_threshold: float
        :type sell_threshold: float
        :returns: A character with the order recommendation.

        """
        crypto_history = robinhood.crypto.get_crypto_historicals(symbol, 
                                                                 interval='5minute', 
                                                                 span='day')
        crypto_history_df = pd.DataFrame(crypto_history)
        crypto_history_df['close_price'] = pd.to_numeric(crypto_history_df['close_price'], errors='coerce')
        crypto_history_df['volume'] = pd.to_numeric(crypto_history_df['volume'], errors='coerce')

        #Calculate the VWAP from the last day in 5 minute intervals.
        #Note: there is a bug that returns 0 in the volume columns!
        #This breaks this algorithm, and is pending fix.
        sum_of_volumes = crypto_history_df['volume'].sum()
        sum_of_prices_times_volumes = crypto_history_df['volume'].dot(crypto_history_df['close_price'])
        vwap = sum_of_prices_times_volumes / sum_of_volumes

        #Get the current market price of the stock.
        current_price = robinhood.crypto.get_crypto_quote(symbol)['ask_price']

        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return None

class TradeBotPairsTrading(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def make_order_recommendation(self, symbol, compared_symbol):
        """
        Makes a recommendation for a market order by comparing
        the prices of two closely related securities. 
        Returns a 'b' if the price of symbol is greater than 
        compared_symbol, a 's' if the price of symbol 
        is less than compared_symbol, or a 'x' if they are equal.

        :param symbol: A ticker symbol.
        :param compared_symbol: The ticker symbol to compare to.
        :type symbol: str
        :type compared_symbol: str
        :returns: A string with the order recommendation.

        """
        pass

class TradeBotCryptoPairsTrading(TradeBotCrypto):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def make_order_recommendation(self, symbol):
        pass

class TradeBotSentimentAnalysis(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)
    
    def make_order_recommendation(self, symbol):
        pass

class TradeBotCryptoSentimentAnalysis(TradeBotCrypto):
    def __init__(self, trade_list):
        TradeBotCrypto.__init__(self, trade_list)

    def make_order_recommendation(self, symbol):
        pass


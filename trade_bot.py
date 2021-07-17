from config import ROBINHOOD_USER, ROBINHOOD_PASS, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import pandas as pd
import robin_stocks.robinhood as robinhood
import tweepy


class TradeBot():
    def __init__(self, trade_list=[]):
        """
        Constructs the TradeBot object with the trade list.

        :param trade_list: A list of ticker symbols.
        :type trade_list: list
        :returns: None

        """
        self.trade_list = trade_list
        # self.robinhood_login()

    def robinhood_login(self):
        """
        Logs user into their Robinhood account.

        :returns: None

        """
        robinhood.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS)

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

    def buy_with_available_funds(self, ticker):
        """
        Buys ticker with all available funds.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: A dictionary.

        """
        available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))

        return robinhood.orders.order_buy_fractional_by_price(ticker, 
                                                              available_funds,
                                                              timeInForce='gfd', 
                                                              extendedHours=False,
                                                              jsonify=True)

    def sell_entire_position(self, ticker):
        """
        Sells entire position in ticker.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: A dictionary.

        """
        portfolio = robinhood.account.build_holdings()
        position = portfolio[ticker]
        equity = float(position['equity'])

        return robinhood.orders.order_sell_fractional_by_price(ticker, 
                                                               equity,
                                                               timeInForce='gfd',
                                                               extendedHours=False,
                                                               jsonify=True)

    def liquidate_portfolio(self):
        """
        Completely liquidates all positions.

        :return: None
        
        """
        portfolio = robinhood.account.build_holdings()

        for ticker, position in portfolio.items():
            equity = float(position['equity'])
            print(ticker, equity)
            robinhood.orders.order_sell_fractional_by_price(ticker, 
                                                            equity,
                                                            timeInForce='gfd',
                                                            extendedHours=False,
                                                            jsonify=True)


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

    def trade(self, amount_in_dollars = 1.00):
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
                    print(f"Sufficient funds are not available for the purchase of {symbol}.") 
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
                    print(f"Sufficient equity is not available for the sale of {symbol}.")
            else:
                print(f"Conditions are not met for either a purchase or a sale of {symbol}.")         


class TradeBotVWAP(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def calculate_VWAP(self, stock_history_df):
        """
        Calculates the Volume-Weighted Average Price (VWAP).

        :param stock_history_df: DataFrame with stock price history,
        :type stock_history_df: DataFrame
        :returns: float

        """
        sum_of_volumes = stock_history_df['volume'].sum()
        sum_of_prices_times_volumes = stock_history_df['volume'].dot(stock_history_df['close_price'])
        vwap = round(sum_of_prices_times_volumes / sum_of_volumes, 2)

        return vwap


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
        vwap = self.calculate_VWAP(stock_history_df)

        #Get the current market price of the stock.
        current_price = float(robinhood.stocks.get_latest_price(symbol, includeExtendedHours=False)[0])

        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return 'x'


class TradeBotPairsTrading(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)

    def make_order_recommendation(self, ticker_1, ticker_2):
        """
        Makes a recommendation for a market order by comparing
        the prices of two closely related securities.
        Returns:
        'b' if the price of ticker_1 is greater than ticker_2
        's' if the price of ticker_1 is less than ticker_2
        'x' if the two prices are equal.
        'b' means buy ticker_1 and sell ticker_2.
        's' means sell ticker_1 and buy ticker_2.
        'x' means sell both ticker_1 and ticker_2.

        :param ticker_1: A ticker symbol.
        :param ticker_2: The ticker symbol to compare to.
        :type ticker: str
        :type ticker_2: str
        :returns: A string with the order recommendation.

        """
        current_price_of_ticker_1 = float(robinhood.stocks.get_latest_price(ticker_1, includeExtendedHours=False)[0])
        current_price_of_ticker_2 = float(robinhood.stocks.get_latest_price(ticker_2, includeExtendedHours=False)[0])

        price_difference = current_price_of_ticker_1 - current_price_of_ticker_2

        if price_difference > 0:
            return 'b'
        elif price_difference < 0:
            return 's'
        else:
            return 'x'

    def trade(self):
        """
        Places buy/sell orders for fractional shares of stock.

        :param amount_in_dollars: The amount to transact with.
        :type amount_in_dollars: float
        :returns: None

        """
        for ticker_pairs in self.trade_list:
            ticker_1 = ticker_pairs[0]
            ticker_2 = ticker_pairs[1]
            action = self.make_order_recommendation(ticker_1, ticker_2)

            if action == 'b':
                # Sell position in ticker_2                                             
                self.sell_entire_position(ticker_2)

                # Buy ticker_1 with all available funds
                self.buy_with_available_funds(ticker_1)

            elif action == 's':
                # Sell position in ticker_1
                self.sell_entire_position(ticker_1)

                # Buy ticker_2 with all available funds
                self.buy_with_available_funds(ticker_2)

            else:
                # Sell ticker_1 and ticker_2
                self.sell_entire_position(ticker_1)
                self.sell_entire_position(ticker_2)


class TradeBotSentimentAnalysis(TradeBot):
    def __init__(self, trade_list):
        TradeBot.__init__(self, trade_list)
    

    def retrieve_tweets(self, ticker):
        """
        Determines if a score is positive, negative, or neutral.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: SearchResults

        """
        consumer_key = TWITTER_CONSUMER_KEY
        consumer_secret = TWITTER_CONSUMER_SECRET

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

        api = tweepy.API(auth)

        query = robinhood.stocks.get_name_by_symbol(ticker)
        public_tweets = api.search(q=query, lang='en', count=1000)

        return public_tweets
    

    def analyze_tweet_sentiments(self, tweets):
        """
        Determines the general consensus on the opinion of the tweets.

        :param tweet: A single tweet or SearchResults object of tweets.
        :type tweet: str or SearchResults
        :returns: DataFrame

        """
        analyzer = SentimentIntensityAnalyzer()

        tweet_sentiments = {'Tweet' : [], 'Score': [], 'Sentiment': []}

        for tweet in tweets:
            score = analyzer.polarity_scores(tweet.text)['compound']
            sentiment = self.determine_sentiment(score)

            tweet_sentiments['Tweet'].append(tweet.text)
            tweet_sentiments['Score'].append(score)
            tweet_sentiments['Sentiment'].append(sentiment)

        tweet_sentiments_df = pd.DataFrame(tweet_sentiments)

        return tweet_sentiments_df


    def determine_sentiment(self, score):
        """
        Determines if a score is positive, negative, or neutral.

        :param score: A sentiment score.
        :type score: float
        :returns: str

        """
        if score >= 0.05:
            return 'POSITIVE'
        elif score <= -0.05:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'


    def make_order_recommendation(self, ticker):
        """
        Makes an order recommendation based on the sentiment of
        1,000 tweets.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: str

        """
        public_tweets = self.retrieve_tweets(ticker)

        
        return None


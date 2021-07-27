from config import ROBINHOOD_USER, ROBINHOOD_PASS, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import pandas as pd
import robin_stocks.robinhood as robinhood
import tweepy


class TradeBot():
    def __init__(self, trade_list):
        """
        Constructs the TradeBot object with the trade list.

        :param trade_list: A list of ticker symbols.
        :type trade_list: list
        :returns: None

        """
        if trade_list is None:
            trade_list = []

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
        # Get portfolio.
        portfolio = robinhood.account.build_holdings()

        # Sell each position in the portfolio.
        for ticker, position in portfolio.items():
            equity = float(position['equity'])
            robinhood.orders.order_sell_fractional_by_price(ticker, 
                                                            equity,
                                                            timeInForce='gfd',
                                                            extendedHours=False,
                                                            jsonify=True)


    def make_order_recommendation(self, ticker):
        """
        For the base class, always returns an 'x'.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: str

        """
        return 'x'
 

    def has_sufficient_funds_available(self, amount_in_dollars):
        """
        Returns a boolean if user's account has enough buying power
        to execute a buy order.

        :param amount_in_dollars: The amount to transact with.
        :type amount_in_dollars: float
        :returns: bool

        """
        # Retrieve the available funds.
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
        for ticker in self.trade_list:
            action = self.make_order_recommendation(ticker)

            if action == 'b':
                if self.has_sufficient_funds_available(amount_in_dollars):
                    print(f"Buying ${amount_in_dollars} of {ticker}...")
                    robinhood.orders.order_buy_fractional_by_price(ticker, 
                                                                   amount_in_dollars, 
                                                                   timeInForce='gfd', 
                                                                   extendedHours=False,
                                                                   jsonify=True)
                    print(f"Successfully bought ${amount_in_dollars} of {ticker}.")
                else:
                    print(f"Sufficient funds are not available for the purchase of {ticker}.") 
            elif action == 's':
                if self.has_sufficient_equity(ticker, amount_in_dollars):
                    print(f"Selling ${amount_in_dollars} of {ticker}...")
                    robinhood.orders.order_sell_fractional_by_price(ticker, 
                                                                    amount_in_dollars, 
                                                                    timeInForce='gfd', 
                                                                    extendedHours=False,
                                                                    jsonify=True)
                    print(f"Successfully sold ${amount_in_dollars} of {ticker}.")
                else:
                    print(f"Sufficient equity is not available for the sale of {ticker}.")
            else:
                print(f"Conditions are not met for either a purchase or a sale of {ticker}.")         


class TradeBotSimpleMovingAverage(TradeBot):
    def __init__(self, trade_list):
        if trade_list is None:
            trade_list = []
        TradeBot.__init__(self, trade_list)


    def calculate_simple_moving_average(self, stock_history_df, number_of_days):
        """
        Calculates the simple moving average based on the number of days.

        :param stock_history_df: DataFrame containing stock history.
        :type stock_history_df: DataFrame
        :param number_of_days: Number of days to calculate the moving average.
        :type number_of_days: int
        :returns: A string with the order recommendation.

        """
        # Typecast the column to numerics.
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')

        # Consider only the last n days.
        n_day_stock_history = stock_history_df.tail(number_of_days)

        # Calculate the moving average.
        n_day_moving_average = round(n_day_stock_history['close_price'].mean(), 2)

        return n_day_moving_average


    def make_order_recommendation(self, ticker):
        """
        Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.
        Returns 'b' for buy, 's' for sell, or 'x' for neither.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: A string with the order recommendation.

        """
        # Construct a DataFrame with the stock history.
        stock_history = robinhood.stocks.get_stock_historicals(ticker, 
                                                               interval='day', 
                                                               span='year' )
        stock_history_df = pd.DataFrame(stock_history)

        # Calculate the 200-day moving average.
        moving_average_200_day = self.calculate_simple_moving_average(stock_history_df, 200)

        # Calculate the 50-day moving average.
        moving_average_50_day = self.calculate_simple_moving_average(stock_history_df, 200)

        # Determine the order recommendation.
        if moving_average_50_day > moving_average_200_day:
            return 'b'
        elif moving_average_50_day < moving_average_200_day:
            return 's'
        else:
            return 'x'


class TradeBotVWAP(TradeBot):
    def __init__(self, trade_list):
        if trade_list is None:
            trade_list = []
        TradeBot.__init__(self, trade_list)

    def calculate_VWAP(self, stock_history_df):
        """
        Calculates the Volume-Weighted Average Price (VWAP).

        :param stock_history_df: DataFrame with stock price history,
        :type stock_history_df: DataFrame
        :returns: float

        """
        # Typecast the columns we need.
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')
        stock_history_df['volume'] = pd.to_numeric(stock_history_df['volume'], errors='coerce')

        # Sum the volumes, and take the dot product of the volume and close_price columns.
        sum_of_volumes = stock_history_df['volume'].sum()
        sum_of_prices_times_volumes = stock_history_df['volume'].dot(stock_history_df['close_price'])

        # Calculate the average.
        vwap = round(sum_of_prices_times_volumes / sum_of_volumes, 2)

        return vwap


    def make_order_recommendation(self, ticker, buy_threshold=0, sell_threshold=0):
        """
        Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.
        Returns 'b' for buy, 's' for sell, or 'x' for neither.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: A string with the order recommendation.

        """
        # Retrieve the stock history and place into a DataFrame.
        stock_history = robinhood.stocks.get_stock_historicals(ticker, 
                                                               interval='5minute', 
                                                               span='day' )
        stock_history_df = pd.DataFrame(stock_history)

        # Calculate the VWAP from the last day in 5 minute intervals.
        vwap = self.calculate_VWAP(stock_history_df)

        # Get the current market price of the stock.
        current_price = float(robinhood.stocks.get_latest_price(ticker, includeExtendedHours=False)[0])

        # Determine the order recommendation.
        if current_price < vwap + buy_threshold:
            return 'b'
        elif current_price > vwap + sell_threshold:
            return 's'
        else:
            return 'x'


class TradeBotPairsTrading(TradeBot):
    def __init__(self, trade_list):
        if trade_list is None:
            trade_list = []
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
        # Get the current prices of both tickers.
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
        if trade_list is None:
            trade_list = []
        TradeBot.__init__(self, trade_list)
    

    def retrieve_tweets(self, ticker):
        """
        Retrieves tweets from Twitter about ticker.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: list

        """
        # Connect to the Twitter API.
        consumer_key = TWITTER_CONSUMER_KEY
        consumer_secret = TWITTER_CONSUMER_SECRET
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        api = tweepy.API(auth)

        # Retrieve the company name represented by ticker.
        query = robinhood.stocks.get_name_by_symbol(ticker)

        # Use the API to search for 1,000 tweets mentioning the company the ticker represents.
        max_count = 1000
        public_tweets = tweepy.Cursor(api.search, q=query, lang='en', tweet_mode = 'extended').items(max_count)

        # Extract the text body of each tweet.
        searched_tweets = []
        for tweet in public_tweets:
            try:
                searched_tweets.append(tweet.retweeted_status.full_text)
            except AttributeError:  # Not a Retweet
                searched_tweets.append(tweet.full_text)

        return searched_tweets
    

    def analyze_tweet_sentiments(self, tweets):
        """
        Analyzes the sentiments of each tweet and returns the average
        sentiment.

        :param tweet: A single tweet or list of tweets.
        :type tweet: str or list
        :returns: float

        """
        analyzer = SentimentIntensityAnalyzer()

        # Initialize an empty DataFrame.
        column_names = ['tweet', 'sentiment_score']
        tweet_sentiments_df = pd.DataFrame(columns=column_names)

        # Get the sentiment score for each tweet and append the text
        # and sentiment_score into the DataFrame.
        for tweet in tweets:
            score = analyzer.polarity_scores(tweet)['compound']
            tweet_sentiment = {'tweet': tweet, 'setiment_score': score}
            tweet_sentiments_df = tweet_sentiments_df.append(tweet_sentiment, ignore_index=True)

        # Calculate the average sentiment score.
        average_sentiment_score = tweet_sentiments_df['sentiment_score'].mean()

        return average_sentiment_score


    def determine_sentiment(self, score):
        """
        Determines if the general sentiment score is positive, negative, or neutral.

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
        20,000 tweets about ticker.

        :param ticker: A ticker symbol.
        :type ticker: str
        :returns: str

        """
        public_tweets = self.retrieve_tweets(ticker)
        consensus = self.analyze_tweet_sentiments(public_tweets)

        if consensus == 'POSITIVE':
            return 'b'
        elif consensus == 'NEGATIVE':
            return 's'
        else:
            return 'x'
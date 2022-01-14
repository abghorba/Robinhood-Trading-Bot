from config import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import pandas as pd
import robin_stocks.robinhood as robinhood
import tweepy


class TradeBot:
    def __init__(self, username, password):
        """Logs user into their Robinhood account."""
        robinhood.login(username, password)

    def robinhood_logout(self):
        """Logs user out of their Robinhood account."""
        return robinhood.logout()

    def has_sufficient_funds_available(self, amount_in_dollars):
        """Returns a boolean if user's account has enough buying
        power to execute a buy order.

        Parameters
        ----------
        amount_in_dollars : float
            The amount in USD to be used for a transaction.

        Returns
        -------
        bool
            True if there are sufficient funds in user's account.

        """
        if not amount_in_dollars:
            return False

        # Retrieve the available funds.
        available_funds = float(
            robinhood.profiles.load_account_profile(info="buying_power")
        )

        return available_funds >= amount_in_dollars

    def has_sufficient_equity(self, ticker, amount_in_dollars):
        """Returns a boolean if user's account has enough equity in
        the given position to execute a sell order.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.
        amount_in_dollars : float
            The amount in USD to be used for a transaction.

        Returns
        -------
        bool
            True if there is sufficient equity in the user's holding.

        """
        if not amount_in_dollars or amount_in_dollars <= 0:
            return False

        portfolio = robinhood.account.build_holdings()
        if ticker in portfolio:
            position = portfolio[ticker]
            equity_in_position = float(position["equity"])
            return equity_in_position >= amount_in_dollars

        return False

    def place_buy_order(self, ticker, amount_in_dollars):
        """Places a buy order for ticker with a specified amount.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.
        amount_in_dollars : float
            The amount in USD to be used for the purchase.

        Returns
        -------
        purchase_data : dict
            Dictionary that contains information regarding the
            purchase of stocks, such as the order id, the state
            of order (queued, confired, filled, failed, canceled,
            etc.), the price, and the quantity.

        """
        purchase_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return purchase_data

        if amount_in_dollars < 1:
            print("ERROR: A purchase cannot be made with less than $1.00 USD.")
            return purchase_data

        # Must have enough funds for the purchase
        if self.has_sufficient_funds_available(amount_in_dollars):
            print(f"Buying ${amount_in_dollars} of {ticker}...")
            purchase_data.update(
                robinhood.orders.order_buy_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully bought ${amount_in_dollars} of {ticker}.")

        return purchase_data

    def place_sell_order(self, ticker, amount_in_dollars):
        """Places a sell order for ticker with a specified amount.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.
        amount_in_dollars : float
            The amount in USD to be used for the sale.

        Returns
        -------
        sale_data : dict
            Dictionary that contains information regarding the
            sale of stocks, such as the order id, the state
            of order (queued, confired, filled, failed, canceled,
            etc.), the price, and the quantity.

        """
        sale_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return sale_data

        if amount_in_dollars < 1:
            print("ERROR: A sale cannot be made with less than $1.00 USD.")
            return sale_data

        # Must have enough equity for the sale
        if self.has_sufficient_equity(ticker, amount_in_dollars):
            print(f"Selling ${amount_in_dollars} of {ticker}...")
            sale_data.update(
                robinhood.orders.order_sell_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully sold ${amount_in_dollars} of {ticker}.")

        return sale_data

    def buy_with_available_funds(self, ticker):
        """Buys ticker with all available funds.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        dict
            Dictionary that contains information regarding the
            purchase of stocks, such as the order id, the state
            of order (queued, confired, filled, failed, canceled,
            etc.), the price, and the quantity.

        """
        if not ticker:
            return {}

        available_funds = float(
            robinhood.profiles.load_account_profile(info="buying_power")
        )
        return self.place_buy_order(ticker, available_funds)

    def sell_entire_position(self, ticker):
        """Sells user's entire position in ticker.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        dict
            Dictionary that contains information regarding the
            sale of stocks, such as the order id, the state
            of order (queued, confired, filled, failed, canceled,
            etc.), the price, and the quantity.

        """
        portfolio = robinhood.account.build_holdings()
        if ticker in portfolio:
            position = portfolio[ticker]
            equity = float(position["equity"])
            return self.place_sell_order(ticker, equity)

        return {}

    def liquidate_portfolio(self):
        """Completely sells all positions held.

        Parameters
        ----------
        None

        Returns
        -------
        compiled_sale_information : list
            A list of dictionaries containing information
            regarding the purchase of stocks, such as the
            order id, the state of order (queued, confired,
            filled, failed, canceled, etc.), the price, and
            the quantity for each position held.

        """
        compiled_sale_information = []
        portfolio = robinhood.account.build_holdings()
        for ticker in portfolio.keys():
            sale_information = self.sell_entire_position(ticker)
            compiled_sale_information.append(sale_information)

        return compiled_sale_information

    def make_order_recommendation(self, ticker):
        """Makes an order recommendation for the given ticker.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        None

        """
        return None

    def trade(self, ticker, amount_in_dollars):
        """Places buy/sell orders for fractional shares of stock.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.
        amount_in_dollars : float
            The amount in USD to be used for a transaction.


        Returns
        -------
        transaction_data : dict
            Dictionary that contains information regarding the
            purchase/sale of stocks, such as the order id, the
            state of order (queued, confired, filled, failed,
            canceled, etc.), the price, and the quantity.

        """
        transaction_data = {}

        action = self.make_order_recommendation(ticker)

        if action == "buy":
            transaction_data.update(self.place_buy_order(ticker, amount_in_dollars))
        elif action == "sell":
            transaction_data.update(self.place_sell_order(ticker, amount_in_dollars))
        else:
            print(
                f"Conditions are not met for either a purchase or a sale of {ticker}."
            )

        return transaction_data


class TradeBotSimpleMovingAverage(TradeBot):
    def calculate_simple_moving_average(self, stock_history_df, number_of_days):
        """Calculates the simple moving average based
        on the number of days.

        Parameters
        ----------
        stock_history_df : pandas.DataFrame
            DataFrame containing the stock's history.
        number_of_days : int
            The number of days used to calculate the n-day moving average.

        Returns
        -------
        n_day_moving_average : float
            The simple moving average for n days.

        """
        if not stock_history_df:
            print("ERROR: Parameters cannot have null values.")
            return 0

        if not number_of_days or number_of_days <= 0:
            print("ERROR: number_of_days must be a positive number.")
            return 0

        # Typecast the column to numerics.
        stock_history_df["close_price"] = pd.to_numeric(
            stock_history_df["close_price"], errors="coerce"
        )

        # Consider only the last n days.
        n_day_stock_history = stock_history_df.tail(number_of_days)

        # Calculate the moving average.
        n_day_moving_average = round(n_day_stock_history["close_price"].mean(), 2)

        return n_day_moving_average

    def make_order_recommendation(self, ticker):
        """Makes a recommendation for a market order by comparing
        the 50-day moving average to the 200-day moving average.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        str
            A string with the order recommendation. Returns
            'buy', 'sell', or None.

        """
        if not ticker:
            print("ERROR: Parameters cannot have null values.")
            return None

        # Construct a DataFrame with the stock history.
        stock_history = robinhood.stocks.get_stock_historicals(
            ticker, interval="day", span="year"
        )
        stock_history_df = pd.DataFrame(stock_history)

        # Calculate the 200-day moving average.
        moving_average_200_day = self.calculate_simple_moving_average(
            stock_history_df, 200
        )

        # Calculate the 50-day moving average.
        moving_average_50_day = self.calculate_simple_moving_average(
            stock_history_df, 50
        )

        # Determine the order recommendation.
        if moving_average_50_day > moving_average_200_day:
            return "buy"
        elif moving_average_50_day < moving_average_200_day:
            return "sell"
        else:
            return None


class TradeBotVWAP(TradeBot):
    def calculate_VWAP(self, stock_history_df):
        """Calculates the Volume-Weighted Average Price (VWAP).

        Parameters
        ----------
        stock_history_df : pandas.DataFrame
            DataFrame containing the stock's history.

        Returns
        -------
        vwap : float
            The calculated Volume-Weighted Average Price.

        """
        if not stock_history_df:
            print("ERROR: Parameters cannot have null values.")
            return 0

        # Typecast the columns we need.
        stock_history_df["close_price"] = pd.to_numeric(
            stock_history_df["close_price"], errors="coerce"
        )
        stock_history_df["volume"] = pd.to_numeric(
            stock_history_df["volume"], errors="coerce"
        )

        # Sum the volumes, and take the dot product of the volume and close_price columns.
        sum_of_volumes = stock_history_df["volume"].sum()
        dot_product_volumes_and_prices = stock_history_df["volume"].dot(
            stock_history_df["close_price"]
        )

        # Calculate the average.
        vwap = round(dot_product_volumes_and_prices / sum_of_volumes, 2)

        return vwap

    def make_order_recommendation(self, ticker):
        """Makes a recommendation for a market order by comparing
        the Volume-Weighted Average Price (VWAP) to the current
        market price.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        str
            A string with the order recommendation. Returns
            'buy', 'sell', or None.

        """
        if not ticker:
            print("ERROR: Parameters cannot have null values.")
            return None

        # Retrieve the stock history and place into a DataFrame.
        stock_history = robinhood.stocks.get_stock_historicals(
            ticker, interval="5minute", span="day"
        )
        stock_history_df = pd.DataFrame(stock_history)

        # Calculate the VWAP from the last day in 5 minute intervals.
        vwap = self.calculate_VWAP(stock_history_df)

        # Get the current market price of the stock.
        current_price = float(
            robinhood.stocks.get_latest_price(ticker, includeExtendedHours=False)[0]
        )

        # Determine the order recommendation.
        if current_price < vwap:
            return "buy"
        elif current_price > vwap:
            return "sell"
        else:
            return None


class TradeBotSentimentAnalysis(TradeBot):
    def retrieve_tweets(self, ticker, max_count=100):
        """Retrieves tweets from Twitter about ticker.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.
        max_count : int
            The maximum number of tweets to retrieve.

        Returns
        -------
        searched_tweets : list
            A list of texts of the retrieved tweets.

        """
        searched_tweets = []

        if not ticker:
            print("ERROR: Parameters cannot have null values.")
            return searched_tweets

        if max_count <= 0:
            print("ERROR: max_count must be a positive number.")
            return searched_tweets

        # Connect to the Twitter API.
        auth = tweepy.AppAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        api = tweepy.API(auth)

        # Retrieve the company name represented by ticker.
        company_name = robinhood.stocks.get_name_by_symbol(ticker)
        query = f"#{company_name} OR ${ticker}"

        # Search for max_counts tweets mentioning the company.
        public_tweets = tweepy.Cursor(
            api.search_tweets,
            q=query,
            lang="en",
            result_type="recent",
            tweet_mode="extended",
        ).items(max_count)

        # Extract the text body of each tweet.
        searched_tweets = []
        for tweet in public_tweets:
            try:
                searched_tweets.append(tweet.retweeted_status.full_text)
            except AttributeError:  # Not a Retweet
                searched_tweets.append(tweet.full_text)

        return searched_tweets

    def analyze_tweet_sentiments(self, tweets):
        """Analyzes the sentiments of each tweet and returns the average
        sentiment.

        Parameters
        ----------
        tweets: list
            A list of the text from tweets.

        Returns
        -------
        average_sentiment_score : float
            The mean of all the sentiment scores from
            the list of tweets.

        """
        if not tweets:
            print("ERROR: Parameters cannot have null values.")
            return 0

        analyzer = SentimentIntensityAnalyzer()

        # Initialize an empty DataFrame.
        column_names = ["tweet", "sentiment_score"]
        tweet_sentiments_df = pd.DataFrame(columns=column_names)

        # Get the sentiment score for each tweet and append the text
        # and sentiment_score into the DataFrame.
        for tweet in tweets:
            score = analyzer.polarity_scores(tweet)["compound"]
            tweet_sentiment = {"tweet": tweet, "sentiment_score": score}
            tweet_sentiments_df = tweet_sentiments_df.append(
                tweet_sentiment, ignore_index=True
            )

        # Calculate the average sentiment score.
        average_sentiment_score = tweet_sentiments_df["sentiment_score"].mean()

        return average_sentiment_score

    def make_order_recommendation(self, ticker):
        """Makes an order recommendation based on the sentiment of
        max_count tweets about ticker.

        Parameters
        ----------
        ticker : str
            A company's ticker symbol.

        Returns
        -------
        str
            A string with the order recommendation. Returns
            'buy', 'sell', or None.

        """
        if not ticker:
            print("ERROR: Parameters cannot have null values.")
            return None

        public_tweets = self.retrieve_tweets(ticker)
        consensus_score = self.analyze_tweet_sentiments(public_tweets)

        if consensus_score >= 0.05:
            return "buy"
        elif consensus_score <= -0.05:
            return "sell"
        else:
            return None


class TradeBotExponentialMovingAverage(TradeBotSimpleMovingAverage):
    pass

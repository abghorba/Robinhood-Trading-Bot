import pandas as pd
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.bots.base_trade_bot import OrderType, TradeBot
from src.utilities import TwitterCredentials

MINIMUM_CONSENSUS_BUY_SCORE = 0.05
MINIMUM_CONSENSUS_SELL_SCORE = -0.05


class TradeBotTwitterSentiments(TradeBot):
    def __init__(self):
        """Logs user into their Robinhood account."""

        super().__init__()

        # Connect to the Twitter API
        twitter_credentials = TwitterCredentials()
        auth = tweepy.AppAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        self.twitter_api = tweepy.API(auth)

        # Set up the sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def retrieve_tweets(self, ticker, max_count=100):
        """
        Retrieves tweets from Twitter about ticker.

        :param ticker: A company's ticker symbol as a string
        :param max_count: The maximum number of tweets to retrieve
        :return: A list of strings of the retrieved tweets
        """

        searched_tweets = []

        if not ticker:
            print("ERROR: param ticker cannot be a null value")
            return searched_tweets

        if max_count <= 0:
            print("ERROR: max_count must be a positive number.")
            return searched_tweets

        # Retrieve the company name represented by ticker.
        company_name = self.get_company_name_from_ticker(ticker)
        query = f"#{company_name} OR ${ticker}"

        # Search for max_counts tweets mentioning the company.
        public_tweets = tweepy.Cursor(
            self.twitter_api.search_tweets,
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

            # Not a Retweet
            except AttributeError:
                searched_tweets.append(tweet.full_text)

        return searched_tweets

    def analyze_tweet_sentiments(self, tweets):
        """
        Analyzes the sentiments of each tweet and returns the average sentiment.

        :param tweets: A list of strings containing the text from tweets
        :return: The mean of all the sentiment scores from the list of tweets
        """

        if not tweets:
            print("ERROR: param tweets cannot be a null value")
            return 0

        # Initialize an empty DataFrame.
        column_names = ["tweet", "sentiment_score"]
        tweet_sentiments_df = pd.DataFrame(columns=column_names)

        # Get the sentiment score for each tweet and append the text and sentiment_score into the DataFrame.
        for tweet in tweets:
            score = self.sentiment_analyzer.polarity_scores(tweet)["compound"]
            tweet_sentiment = {"tweet": tweet, "sentiment_score": score}
            tweet_sentiments_df = pd.concat(
                [tweet_sentiments_df, pd.DataFrame([tweet_sentiment])],
                ignore_index=True,
            )

        # Calculate the average sentiment score.
        average_sentiment_score = tweet_sentiments_df["sentiment_score"].mean()

        return average_sentiment_score

    def make_order_recommendation(self, ticker):
        """
        Makes an order recommendation based on the sentiment of max_count tweets about ticker.

        :param ticker: A company's ticker symbol as a string
        :return: OrderType recommendation
        """

        if not ticker:
            print("ERROR: param ticker cannot be a null value")
            return None

        public_tweets = self.retrieve_tweets(ticker)
        consensus_score = self.analyze_tweet_sentiments(public_tweets)

        # Determine the order recommendation.
        if consensus_score >= MINIMUM_CONSENSUS_BUY_SCORE:
            return OrderType.BUY_RECOMMENDATION

        elif consensus_score <= MINIMUM_CONSENSUS_SELL_SCORE:
            return OrderType.SELL_RECOMMENDATION

        else:
            return OrderType.HOLD_RECOMMENDATION

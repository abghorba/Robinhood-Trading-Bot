import random

import pytest

from src.trading_bots.twitter_sentiments import TradeBotTwitterSentiments


class TestTradeBotTwitterSentimentAnalysis:
    trade_bot = TradeBotTwitterSentiments()

    ##########################################################################
    @pytest.mark.parametrize(
        "ticker,company_name,max_count",
        [("GME", "GameStop", 100), ("AAPL", "Apple", 150), ("AMZN", "Amazon", 200)],
    )
    def test_retrieve_tweets(self, ticker, company_name, max_count):
        public_tweets = self.trade_bot.retrieve_tweets(ticker, max_count)

        assert isinstance(public_tweets, list)
        assert len(public_tweets) == max_count

        for _ in range(5):
            random_index = random.randint(0, len(public_tweets))
            current_tweet = public_tweets[random_index].lower()
            assert company_name.lower() in current_tweet or ticker.lower() in current_tweet

    ##########################################################################
    @pytest.mark.parametrize(
        "ticker",
        [
            "GME",
            "AAPL",
            "AMZN",
        ],
    )
    def test_analyze_tweet_sentiments(self, ticker):
        public_tweets = self.trade_bot.retrieve_tweets(ticker)
        average_sentiment_score = self.trade_bot.analyze_tweet_sentiments(public_tweets)
        assert -1 <= average_sentiment_score <= 1

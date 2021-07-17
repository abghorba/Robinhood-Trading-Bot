import robin_stocks.robinhood as robinhood
import pandas as pd
import os
import trade_bot
import tweepy
from config import ROBINHOOD_USER, ROBINHOOD_PASS, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def robinhood_login():
    robinhood.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS)

def main():
    robinhood_login()

    # stock_trade_list = ['AAPL', 'ENPH']
    # crypto_trade_list = ['BTC', 'DOGE']

    # tradebot = trade_bot.TradeBot(stock_trade_list)
    # order = tradebot.liquidate_portfolio()

    auth = tweepy.AppAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)

    api = tweepy.API(auth)

    tweet_count = 10000
    query = robinhood.stocks.get_name_by_symbol('FB')
    public_tweets = api.search(q=query, lang='en', count=tweet_count)
    print(public_tweets[31].text)

    analyzer = SentimentIntensityAnalyzer()

    tweet_sentiments = {'Tweet' : [], 'Score': [], 'Sentiment': []}

    for tweet in public_tweets:
        score = analyzer.polarity_scores(tweet.text)['compound']
        if score >= 0.05:
            sentiment = 'POSITIVE'
        elif score <= -0.05:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'

        tweet_sentiments['Tweet'].append(tweet.text)
        tweet_sentiments['Score'].append(score)
        tweet_sentiments['Sentiment'].append(sentiment)

    tweet_sentiments_df = pd.DataFrame(tweet_sentiments)

    print(tweet_sentiments_df[4])

if __name__ == "__main__":
    main()
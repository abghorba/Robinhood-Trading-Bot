from config import ROBINHOOD_USER, ROBINHOOD_PASS
from pandas.core.frame import DataFrame
from tweepy.models import SearchResults

import pandas as pd
import random
import robin_stocks.robinhood as robinhood
import trade_bot

sample_stock_list = ['AAPL', 'MSFT', 'AMZN']
sample_stock_list2 = ['FB', 'GOOG', 'TSLA']

robinhood.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS)

class TestTradeBot():    
    def test_get_current_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        assert test_bot.get_current_trade_list() == sample_stock_list
    

    def test_update_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        test_bot.update_trade_list(sample_stock_list2)
        assert test_bot.get_current_trade_list() == sample_stock_list2


    def test_buy_with_available_funds(self):
        test_bot = trade_bot.TradeBot()
        available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))

        if available_funds >= 1.00:
            test_bot.buy_with_available_funds('AAPL')
            available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))
            assert available_funds == 0
        else:
            assert True


    def test_sell_entire_position(self):
        test_bot = trade_bot.TradeBot()
        test_bot.sell_entire_position('AAPL')
        current_portfolio = robinhood.account.build_holdings()

        assert 'AAPL' not in current_portfolio


    def test_liquidate_portfolio(self):
        test_bot = trade_bot.TradeBot()
        test_bot.liquidate_portfolio()
        current_portfolio = robinhood.account.build_holdings()
        
        assert len(current_portfolio) == 0


    def test_make_order_recommendation(self):
        test_bot = trade_bot.TradeBot()
        recommend_1 = test_bot.make_order_recommendation('AAPL')
        recommend_2 = test_bot.make_order_recommendation('BABA')

        assert recommend_1 == 'x'
        assert recommend_2 == 'x'
    

    def test_has_sufficient_funds_available(self):
        test_bot = trade_bot.TradeBot()
        available_funds = float(robinhood.profiles.load_account_profile(info="buying_power"))

        assert test_bot.has_sufficient_funds_available(5.00) == (available_funds >= 5.00)
        assert test_bot.has_sufficient_funds_available(1.00) == (available_funds >= 1.00)


    def test_has_sufficient_equity(self):
        test_bot = trade_bot.TradeBot()


    def test_trade(self):
        pass


class TestTradeBotSimpleMovingAverage():
    def test_calculate_simple_moving_average(self):
        test_bot = trade_bot.TradeBotSimpleMovingAverage()

        stock_history = {'begins_at': ['2021-07-16T13:15:00Z', '2021-07-16T13:20:00Z', '2021-07-16T13:25:00Z',
                                       '2021-07-16T13:30:00Z', '2021-07-16T13:35:00Z', '2021-07-16T13:40:00Z',
                                       '2021-07-16T13:45:00Z', '2021-07-16T13:50:00Z', '2021-07-16T13:55:00Z',],
                         'open_price': ['100.01', '105.01', '102.76', '99.32', '98.78', '100.43', '100.97', '105.44', '103.72'],
                         'close_price': ['105.01', '102.76', '99.32', '98.78', '100.43', '100.97', '105.44', '103.72', '101.22'],
                         'high_price': ['105.25', '105.33', '103.22', '99.32', '102.22', '100.97', '105.88', '107.32', '105.33'],
                         'low_price': ['99.24', '101.23', '98.34', '97.45', '97.53', '100.21', '99.34', '102.21', '100.22'],
                         'volume': ['876543', '2355212', '753662', '546422', '876542', '2355635', '556774', '567876', '2234563'],
                         'session': ['reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg'],
                         'interpolated': ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False'],
                         'symbol': ['TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST']
                         }
        stock_history_df = pd.DataFrame(stock_history)

        moving_average_3_day = test_bot.calculate_simple_moving_average(stock_history_df, 3)
        moving_average_5_day = test_bot.calculate_simple_moving_average(stock_history_df, 5)
        moving_average_9_day = test_bot.calculate_simple_moving_average(stock_history_df, 9)

        assert moving_average_3_day == 103.46
        assert moving_average_5_day == 102.36
        assert moving_average_9_day == 101.96


    def test_make_order_recommendation(self):
        pass


class TestTradeBotVWAP():
    def test_calculate_VWAP(self):
        test_bot = trade_bot.TradeBotVWAP(sample_stock_list)

        stock_history = {'begins_at': ['2021-07-16T13:15:00Z', '2021-07-16T13:20:00Z', '2021-07-16T13:25:00Z',
                                       '2021-07-16T13:30:00Z', '2021-07-16T13:35:00Z', '2021-07-16T13:40:00Z',
                                       '2021-07-16T13:45:00Z', '2021-07-16T13:50:00Z', '2021-07-16T13:55:00Z',],
                         'open_price': ['100.01', '105.01', '102.76', '99.32', '98.78', '100.43', '100.97', '105.44', '103.72'],
                         'close_price': ['105.01', '102.76', '99.32', '98.78', '100.43', '100.97', '105.44', '103.72', '101.22'],
                         'high_price': ['105.25', '105.33', '103.22', '99.32', '102.22', '100.97', '105.88', '107.32', '105.33'],
                         'low_price': ['99.24', '101.23', '98.34', '97.45', '97.53', '100.21', '99.34', '102.21', '100.22'],
                         'volume': ['876543', '2355212', '753662', '546422', '876542', '2355635', '556774', '567876', '2234563'],
                         'session': ['reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg', 'reg'],
                         'interpolated': ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False'],
                         'symbol': ['TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST', 'TEST']
                         }

        stock_history_df = pd.DataFrame(stock_history)
        stock_history_df['close_price'] = pd.to_numeric(stock_history_df['close_price'], errors='coerce')
        stock_history_df['volume'] = pd.to_numeric(stock_history_df['volume'], errors='coerce')
        sum_volumes = stock_history_df['volume'].sum()
        sum_prices_times_volumes =  sum([x*y for x,y in zip(stock_history['volume'], stock_history['close_price'])])
        vwap = round(sum_volumes/sum_prices_times_volumes, 2)

        assert vwap == test_bot.calculate_VWAP(stock_history_df)


class TestTradeBotSentimentAnalysis():
    def test_retrieve_tweets(self):
        test_bot = trade_bot.TradeBotSentimentAnalysis()

        ticker = 'GME'

        public_tweets = test_bot.retrieve_tweets(ticker)
        assert isinstance(public_tweets, list)

        max_count = 1000

        assert len(public_tweets) == max_count

        company = robinhood.stocks.get_name_by_symbol(ticker)
        random_index = random.randint(0, max_count)
        assert company in public_tweets[random_index]
            

    def test_analyze_tweet_sentiments(self):
        test_bot = trade_bot.TradeBotSentimentAnalysis()

        ticker = 'AMC'

        public_tweets = test_bot.retrieve_tweets(ticker)
        average_sentiment_score = test_bot.analyze_tweet_sentiments(public_tweets)

        assert isinstance(average_sentiment_score, float)
        assert -1 <= average_sentiment_score <= 1
        

    def test_determine_sentiment(self):
        test_bot = trade_bot.TradeBotSentimentAnalysis()

        assert test_bot.determine_sentiment(0.00) == 'NEUTRAL'
        assert test_bot.determine_sentiment(-0.05) == 'NEGATIVE'
        assert test_bot.determine_sentiment(0.05) == 'POSITIVE'
        assert test_bot.determine_sentiment(0.25) == 'POSITIVE'
        assert test_bot.determine_sentiment(-0.33) == 'NEGATIVE'
        assert test_bot.determine_sentiment(-0.02) == 'NEUTRAL'
        assert test_bot.determine_sentiment(0.03) == 'NEUTRAL'


    def test_make_order_recommendation(self):
        test_bot = trade_bot.TradeBotSentimentAnalysis()

        ticker = 'BABA'

        public_tweets = test_bot.retrieve_tweets(ticker)
        average_sentiment_score = test_bot.analyze_tweet_sentiments(public_tweets)
        consensus = test_bot.determine_sentiment(average_sentiment_score)

        recommendation = test_bot.make_order_recommendation(ticker)

        if consensus == 'POSITIVE':
            assert recommendation == 'b'
        elif consensus == 'NEGATIVE':
            assert recommendation == 's'
        else:
            assert recommendation == 'x'
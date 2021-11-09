from config import ROBINHOOD_USER, ROBINHOOD_PASS

import pandas as pd
import pytest
import random
import robin_stocks.robinhood as robinhood
import time
import trade_bot as tb

@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(1)

class TestTradeBot():
    trade_bot = tb.TradeBot()

    def test_robinhood_login_is_successful(self):
        login_data = self.trade_bot.robinhood_login(ROBINHOOD_USER, ROBINHOOD_PASS)
        assert isinstance(login_data, dict)
        assert len(login_data) > 0


    # The test account has been initialized with $5.15.
    @pytest.mark.parametrize(
        "amount_in_dollars,expected",
        [
            (0, False), (0.99, True),
            (1, True), (1.15, True),
            (5, True), (5.15, True),
            (5.16, False), (10.01, False),
            (15.00, False), ("", False)
        ]
    )
    def test_has_sufficient_funds_available(self, amount_in_dollars, expected):
        has_funds = self.trade_bot.has_sufficient_funds_available(amount_in_dollars)
        assert has_funds == expected


    # Purchase $3 of AAPL and $2.15 of GOOG.
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ('AAPL', 0, False), ('AAPL', 0.99, False),
            ('AAPL', 10, False), ('AAPL', 3, True), 
            ('GOOG', 3, False), ('GOOG', 2.15, True), 
            ('', 1.00, False), ('', 0.99, False),
            ('AAPL', '', False), ('', '', False)
        ]
    )
    def test_place_buy_order(self, ticker, amount_in_dollars, expected):
        purchase_data = self.trade_bot.place_buy_order(ticker, amount_in_dollars)
        assert (len(purchase_data) > 0) == expected


    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ('AAPL', 0.00, False), ('AAPL', 0.50, True),
            ('AAPL', 2.50, True), ('GOOG', 1, True),
            ('AAPL', 9.99, False), ('GOOG', 3, False),
            ('FB', 5, False), ('AAPL', '', False),
            ('', 2, False), ('', '', False)
        ]
    )
    def test_has_sufficient_equity(self, ticker, amount_in_dollars, expected):
        has_equity = self.trade_bot.has_sufficient_equity(ticker, amount_in_dollars)
        assert has_equity == expected


    # Sell $1.50 of AAPL and $1 of GOOG.
    # Left with $1.50 in AAPL and $1.15 in GOOG,
    # assuming no price fluctuations.
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ('AAPL', 0.00, False), ('AAPL', 0.50, False),
            ('AAPL', 5, False), ('GOOG', 5, False),
            ('AAPL', 1.50, True), ('GOOG', 1, True),
            ('FB', 5, False), ('AAPL', '', False),
            ('', 2, False), ('', '', False)
        ]
    )
    def test_place_sell_order(self, ticker, amount_in_dollars, expected):
        sale_data = self.trade_bot.place_sell_order(ticker, amount_in_dollars)
        assert (len(sale_data)> 0) == expected


    # Commit all available funds to a position in MSFT.
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("", False), ("MSFT", True), ("AMZN", False)
        ]
    )
    def test_buy_with_available_funds(self, ticker, expected):
        purchase_data = self.trade_bot.buy_with_available_funds(ticker)
        assert (len(purchase_data) > 0) == expected

        # Check that all the funds were used.
        if len(purchase_data) > 0:
            available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))
            assert available_funds == 0


    # Completely sell out of the position in MSFT.
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("", False), ("MSFT", True), ("MSFT", False)
        ]
    )
    def test_sell_entire_position(self, ticker, expected):
        sale_data = self.trade_bot.sell_entire_position(ticker)
        assert (len(sale_data) > 0) == expected

        # Check that the position no longer exists in the portfolio.
        if len(sale_data) > 0:
            portfolio = robinhood.account.build_holdings()
            assert ticker not in portfolio


    # Sell off all current holdings.
    @pytest.mark.parametrize(
        "expected",
        [
            (True), (False)
        ]
    )
    def test_liquidate_porfolio(self, expected):
        compiled_sale_data = self.trade_bot.liquidate_portfolio()
        assert len(compiled_sale_data) == expected

        # Check that user's portfolio is empty.
        if len(compiled_sale_data) > 0:
            portfolio = robinhood.account.build_holdings()
            assert len(portfolio) == 0


class TestTradeBotSimpleMovingAverage():
    trade_bot = tb.TradeBotSimpleMovingAverage()

    @pytest.mark.parametrize(
        "number_of_days,expected",
        [
            (3, 103.46), (5, 102.36), (9, 101.96)
        ]
    )
    def test_calculate_simple_moving_average(self, number_of_days, expected):
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
        moving_average = self.trade_bot.calculate_simple_moving_average(stock_history_df, number_of_days)
        assert moving_average == expected


    def test_make_order_recommendation(self):
        pass


class TestTradeBotVWAP():
    trade_bot = tb.TradeBotVWAP()

    def test_calculate_VWAP(self):
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
        dot_product_volumes_and_prices =  sum([x*y for x,y in zip(stock_history_df['volume'], stock_history_df['close_price'])])
        vwap = round(dot_product_volumes_and_prices/sum_volumes, 2)

        assert vwap == self.trade_bot.calculate_VWAP(stock_history_df)


    def test_make_order_recommendation(self):
        pass


class TestTradeBotSentimentAnalysis():
    trade_bot = tb.TradeBotSentimentAnalysis()

    @pytest.mark.parametrize(
        "ticker,max_count",
        [
            ('GME', 100), ('AAPL', 300), ('TWTR', 200)
        ]
    )
    def test_retrieve_tweets(self, ticker, max_count):
        public_tweets = self.trade_bot.retrieve_tweets(ticker, max_count)
        assert isinstance(public_tweets, list)
        assert len(public_tweets) == max_count
        company = robinhood.stocks.get_name_by_symbol(ticker)
        for _ in range(5):
            random_index = random.randint(0, max_count)
            assert company in public_tweets[random_index]
            

    def test_analyze_tweet_sentiments(self):
        ticker = 'AMC'
        public_tweets = self.trade_bot.retrieve_tweets(ticker)
        average_sentiment_score = self.trade_bot.analyze_tweet_sentiments(public_tweets)
        assert isinstance(average_sentiment_score, float)
        assert -1 <= average_sentiment_score <= 1
        

    @pytest.mark.parametrize(
        "ticker",
        [
            ('BABA'), ('TSLA'), ('GME')
        ]
    )
    def test_make_order_recommendation(self, ticker):
        public_tweets = self.trade_bot.retrieve_tweets(ticker)
        consensus_score = self.trade_bot.analyze_tweet_sentiments(public_tweets)
        recommendation = self.trade_bot.make_order_recommendation(ticker)

        if consensus_score >= 0.05:
            assert recommendation == 'buy'
        elif consensus_score <= -0.05:
            assert recommendation == 'sell'
        else:
            assert recommendation is None


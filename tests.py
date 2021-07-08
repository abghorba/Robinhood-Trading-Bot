import pytest
import trade_bot
import os
import robin_stocks.robinhood as robinhood

sample_stock_list = ['AAPL', 'MSFT', 'AMZN']
sample_stock_list2 = ['FB', 'GOOG', 'TSLA']
sample_crypto_list = ['BTC', 'ETH']
sample_crypto_list2 = ['BTC', 'DOGE']

robin_user = os.environ.get("robinhood_username")
robin_pass = os.environ.get("robinhood_password")

robinhood.login(username=robin_user,
                password=robin_pass,
                expiresIn=86400,
                by_sms=True)

class TestTradeBot():    
    def test_get_current_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        assert test_bot.get_current_trade_list() == sample_stock_list
    
    def test_update_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        test_bot.update_trade_list(sample_stock_list2)
        assert test_bot.get_current_trade_list() == sample_stock_list2

    def test_buy_with_available_funds(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))
        test_bot.buy_with_available_funds('AAPL')
        available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))

        assert available_funds == 0

    def test_sell_entire_position(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        test_bot.sell_entire_position('AAPL')
        current_portfolio = robinhood.account.build_holdings()

        assert 'AAPL' not in current_portfolio

    def test_liquidate_portfolio(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        test_bot.liquidate_portfolio()
        current_portfolio = robinhood.account.build_holdings()
        
        assert len(current_portfolio) == 0

    def test_make_order_recommendation(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        recommend_1 = test_bot.make_order_recommendation('AAPL')
        recommend_2 = test_bot.make_order_recommendation('BABA')

        assert recommend_1 in {'x', 'b', 's'}
        assert recommend_2 in {'x', 'b', 's'}
    
    def test_has_sufficient_funds_available(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        available_funds = float(robinhood.profiles.load_account_profile(info="buying_power"))

        assert test_bot.has_sufficient_funds_available(5.00) == (available_funds >= 5.00)
        assert test_bot.has_sufficient_funds_available(1.00) == (available_funds >= 1.00)

    def test_has_sufficient_equity(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)

    def test_trade(self):
        pass
    
class TestTradeBotCrypto():    
    def test_get_current_trade_list(self):
        test_bot = trade_bot.TradeBotCrypto(sample_crypto_list)
        assert test_bot.get_current_trade_list() == sample_crypto_list
    
    def test_update_trade_list(self):
        test_bot = trade_bot.TradeBotCrypto(sample_crypto_list)
        test_bot.update_trade_list(sample_crypto_list2)
        assert test_bot.get_current_trade_list() == sample_crypto_list2

    def test_make_order_recommendation(self):
        pass
    
    def test_trade(self):
        pass
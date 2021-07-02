import pytest
import trade_bot

sample_stock_list = ['AAPL', 'MSFT', 'AMZN']
sample_stock_list2 = ['FB', 'GOOG', 'TSLA']
sample_crypto_list = ['BTC', 'ETH']
sample_crypto_list2 = ['BTC', 'DOGE']

class TestTradeBot():    
    def test_get_current_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        assert test_bot.get_current_trade_list() == sample_stock_list
    
    def test_update_trade_list(self):
        test_bot = trade_bot.TradeBot(sample_stock_list)
        test_bot.update_trade_list(sample_stock_list2)
        assert test_bot.get_current_trade_list() == sample_stock_list2
    

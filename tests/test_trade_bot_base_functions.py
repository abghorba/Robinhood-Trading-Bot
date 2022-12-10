import pytest
import robin_stocks.robinhood as robinhood
import time

from src.trading_bots.base import TradeBot
from src.trading_bots.utilities import ROBINHOOD_PASS, ROBINHOOD_USER
from tests.configs import TestMode


# DISCLAIMER: ONLY CHANGE BELOW TEST MODE IF YOU UNDERSTAND THAT THIS TEST 
# WILL BE MAKING MARKET ORDERS ON YOUR BEHALF. THIS IS FOR TESTING PURPOSES 
# ONLY AND IS NOT MEANT TO BE FINANCIAL ADVICE. YOU MAY LOSE (PART OF) YOUR
# INVESTMENT THROUGH THE DURATION OF THIS TEST
TEST_MODE = TestMode.SKIP_MARKET_ORDERS
MIN_CASH_TO_RUN_TEST = 5


@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(1)


class TestTradeBot:

    print("WARNING: Be advised that this test will send REAL market orders with REAL money!")
    print("WARNING: This test could also result in your account being marked for day trading!")

    trade_bot = TradeBot(ROBINHOOD_USER, ROBINHOOD_PASS)
    current_funds = trade_bot.get_current_cash_position()
    enough_funds_to_run_test = True if current_funds >= MIN_CASH_TO_RUN_TEST else False

    ##########################################################################
    def test_get_current_positions(self):
        portfolio = self.trade_bot.get_current_positions()
        assert isinstance(portfolio, dict)

    ##########################################################################
    def test_get_current_cash_position(self):
        cash_position = self.trade_bot.get_current_cash_position()
        assert isinstance(cash_position, float)
        assert cash_position >= 0.00

    ##########################################################################
    @pytest.mark.parametrize(
        "ticker",
        [
            # Invalid Parameters
            "",

            # Valid Parameters
            "AAPL",
            "GOOG",
            "META",
        ]
    )
    def test_get_current_market_price(self, ticker):
        market_price = self.trade_bot.get_current_market_price(ticker)
        assert isinstance(market_price, float)
        assert market_price >= 0.00

    ##########################################################################
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            # Invalid Parameters
            ("", ""),

            # Valid Parameters
            ("AAPL", "Apple"),
            ("GOOG", "Alphabet Class C"),
            ("META", "Meta Platforms")
        ]
    )   
    def test_get_company_name_from_ticker(self, ticker, expected):
        company_name = self.trade_bot.get_company_name_from_ticker(ticker)
        assert company_name == expected

    ##########################################################################
    @pytest.mark.parametrize(
        "ticker,interval,time_span",
        [
            # Invalid Parameters
            ("", "", ""),
            ("", "hour", ""),
            ("", "", "month"),
            ("", "hour", "month"),
            ("", "30minute", ""),
            ("", "", "2year"),

            # Valid Parameters
            ("AAPL", "", ""),
            ("AAPL", "5minute", "month"),
            ("AAPL", "hour", "year"),
            ("AAPL", "day", "5year"),
        ]
    )
    def test_get_stock_history_dataframe(self, ticker, interval, time_span):
        
        if not interval or not time_span:
            # Use default parameters of interval="day" and time_span="year"
            stock_history_df = self.trade_bot.get_stock_history_dataframe(ticker)
        else:
            stock_history_df = self.trade_bot.get_stock_history_dataframe(ticker,
                                                                          interval="day",
                                                                          time_span="year")
        
        assert not stock_history_df.empty if ticker else stock_history_df.empty

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "amount_in_dollars,expected",
        [
            # Invalid Parameters
            ("", False),
            (0, False),

            # Valid Parameters
            (0.99, True),
            (1, True),
            (4.99, True),
            (current_funds, True),
            (current_funds + 0.01, False),
            (current_funds + 5.01, False),
        ]
    )
    def test_has_sufficient_funds_available(self, amount_in_dollars, expected):
        """Checks there are enough funds in the portfolio"""

        has_funds = self.trade_bot.has_sufficient_funds_available(amount_in_dollars)
        assert has_funds == expected

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            # Invalid Parameters
            ('', '', False),
            ('AAPL', '', False),
            ('', 1.00, False),
            ('AAPL', 0, False),
            ('AAPL', 0.99, False),

            # Valid Parameters
            ('AAPL', current_funds + .01, False),
            ('AAPL', 5, True), 
        ]
    )
    def test_place_buy_order(self, ticker, amount_in_dollars, expected):
        """Spends $5 of cash on AAPL"""

        purchase_data = self.trade_bot.place_buy_order(ticker, amount_in_dollars)
        assert (len(purchase_data) > 0) == expected

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            # Invalid Parameters
            ('AAPL', '', False),
            ('', 2, False),
            ('', '', False),
            ('AAPL', 0.00, False),

            # Valid Parameters
            ('AAPL', 2.50, True),
            ('AAPL', 5, False),
            ('AAPL', 5.01, False),
            ('GOOG', 5, False),
        ]
    )
    def test_has_sufficient_equity(self, ticker, amount_in_dollars, expected):
        has_equity = self.trade_bot.has_sufficient_equity(ticker, amount_in_dollars)
        assert has_equity == expected

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            # Invalid Parameters
            ('AAPL', '', False),
            ('', 2, False),
            ('', '', False),
            ('AAPL', 0.00, False),
            ('AAPL', 0.50, False),

            # Valid Parameters
            ('AAPL', 3, True),
            ('GOOG', 1, False),
            ('FB', 5, False),
        ]
    )
    def test_place_sell_order(self, ticker, amount_in_dollars, expected):
        """
        Sell $3 of AAPL stock, leaving a $2 position in AAPL (assuming 
        no price fluctuations)
        """

        sale_data = self.trade_bot.place_sell_order(ticker, amount_in_dollars)
        assert (len(sale_data)> 0) == expected

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("", False),
            ("MSFT", True),
            ("AMZN", False)
        ]
    )
    def test_buy_with_available_funds(self, ticker, expected):
        """Commit all available funds to a position in MSFT"""

        purchase_data = self.trade_bot.buy_with_available_funds(ticker)
        assert (len(purchase_data) > 0) == expected

        # Check that all the funds were used.
        if len(purchase_data) > 0:
            available_funds = float(robinhood.profiles.load_account_profile(info='buying_power'))
            assert available_funds == 0

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("", False),
            ("MSFT", True),
            ("MSFT", False)
        ]
    )
    def test_sell_entire_position(self, ticker, expected):
        """Completely sell out of the position in MSFT"""

        sale_data = self.trade_bot.sell_entire_position(ticker)
        assert (len(sale_data) > 0) == expected

        # Check that the position no longer exists in the portfolio.
        if len(sale_data) > 0:
            portfolio = self.trade_bot.get_current_positions()
            assert ticker not in portfolio

    ##########################################################################
    @pytest.mark.skipif(TEST_MODE == TestMode.SKIP_MARKET_ORDERS,
                        reason="Current TestMode selected will skip this test!")
    @pytest.mark.skipif(not enough_funds_to_run_test, 
                        reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "expected",
        [
            True,
            False,
        ]
    )
    def test_liquidate_portfolio(self, expected):
        """Sell out of all current holdings"""

        compiled_sale_data = self.trade_bot.liquidate_portfolio()
        assert len(compiled_sale_data) == expected

        # Check that user's portfolio is empty.
        if len(compiled_sale_data) > 0:
            portfolio = self.trade_bot.get_current_positions()
            assert len(portfolio) == 0

import pytest

from src.bots.base_trade_bot import TradeBot
from src.utilities import RobinhoodCredentials
from tests.configs import _TestMode

# DISCLAIMER: ONLY CHANGE BELOW TEST MODE IF YOU UNDERSTAND THAT THIS TEST
# WILL BE MAKING MARKET ORDERS ON YOUR BEHALF. THIS IS FOR TESTING PURPOSES
# ONLY AND IS NOT MEANT TO BE FINANCIAL ADVICE. YOU MAY LOSE (PART OF) YOUR
# INVESTMENT THROUGH THE DURATION OF THIS TEST
TEST_MODE = _TestMode.SKIP_ALL_MARKET_ORDERS
MIN_CASH_TO_RUN_TEST = 5


@pytest.mark.skipif(RobinhoodCredentials().empty_credentials, reason="Robinhood credentials not provided!")
class TestTradeBot:
    print("WARNING: Be advised that this test will send REAL market orders with REAL money!")
    print("WARNING: This test could also result in your account being marked for day trading!")

    trade_bot = TradeBot()
    current_funds = trade_bot.get_current_cash_position()
    enough_funds_to_run_test = True if current_funds >= MIN_CASH_TO_RUN_TEST else False

    def test_get_current_positions(self):
        """Tests TradeBot.get_current_positions()."""

        portfolio = self.trade_bot.get_current_positions()
        assert isinstance(portfolio, dict)

    def test_get_current_cash_position(self):
        """Tests TradeBot.get_current_cash_position()."""

        cash_position = self.trade_bot.get_current_cash_position()
        assert isinstance(cash_position, float)
        assert cash_position >= 0.00

    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "amount_in_dollars,expected",
        [
            ("", False),
            (0, False),
            (0.99, True),
            (1, True),
            (current_funds - 0.01, True),
            (current_funds, True),
            (current_funds + 0.01, False),
        ],
    )
    def test_has_sufficient_funds_available(self, amount_in_dollars, expected):
        """Tests TradeBot.has_sufficient_funds_available()."""

        assert self.trade_bot.has_sufficient_funds_available(amount_in_dollars) == expected

    @pytest.mark.parametrize(
        "ticker",
        ["", "AAPL", "GOOG", "META"],
    )
    def test_get_current_market_price(self, ticker):
        """Tests TradeBot.get_current_market_price()."""

        market_price = self.trade_bot.get_current_market_price(ticker)
        assert isinstance(market_price, float)
        assert market_price >= 0.00

    @pytest.mark.parametrize(
        "ticker,expected",
        [
            # Invalid Parameters
            ("", ""),
            # Valid Parameters
            ("AAPL", "Apple"),
            ("GOOG", "Alphabet Class C"),
            ("META", "Meta Platforms"),
        ],
    )
    def test_get_company_name_from_ticker(self, ticker, expected):
        """Tests TradeBot.get_company_name_from_ticker()."""

        assert self.trade_bot.get_company_name_from_ticker(ticker) == expected

    @pytest.mark.parametrize(
        "ticker,interval,time_span,empty_dataframe",
        [
            ("", "day", "year", True),
            ("AAPL", "30minute", "year", True),
            ("AAPL", "day", "6month", True),
            ("AAPL", "5minute", "day", False),
            ("AAPL", "5minute", "week", False),
            ("AAPL", "5minute", "month", False),
            ("AAPL", "5minute", "3month", False),
            ("AAPL", "5minute", "year", False),
            ("AAPL", "5minute", "5year", False),
            ("AAPL", "10minute", "day", False),
            ("AAPL", "10minute", "week", False),
            ("AAPL", "10minute", "month", False),
            ("AAPL", "10minute", "3month", False),
            ("AAPL", "10minute", "year", False),
            ("AAPL", "10minute", "5year", False),
            ("AAPL", "hour", "day", False),
            ("AAPL", "hour", "week", False),
            ("AAPL", "hour", "month", False),
            ("AAPL", "hour", "3month", False),
            ("AAPL", "hour", "year", False),
            ("AAPL", "hour", "5year", False),
            ("AAPL", "day", "day", False),
            ("AAPL", "day", "week", False),
            ("AAPL", "day", "month", False),
            ("AAPL", "day", "3month", False),
            ("AAPL", "day", "year", False),
            ("AAPL", "day", "5year", False),
            ("AAPL", "week", "day", False),
            ("AAPL", "week", "week", False),
            ("AAPL", "week", "month", False),
            ("AAPL", "week", "3month", False),
            ("AAPL", "week", "year", False),
            ("AAPL", "week", "5year", False),
        ],
    )
    def test_get_stock_history_dataframe(self, ticker, interval, time_span, empty_dataframe):
        """Tests TradeBot.get_stock_history_dataframe()."""

        stock_history_df = self.trade_bot.get_stock_history_dataframe(ticker, interval=interval, time_span=time_span)

        assert stock_history_df.empty if empty_dataframe else not stock_history_df.empty

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ("", "", False),
            ("AAPL", "", False),
            ("", 1, False),
            ("AAPL", 0.99, False),
            ("AAPL", trade_bot.get_current_cash_position() + 0.01, False),
            ("AAPL", MIN_CASH_TO_RUN_TEST, True),
        ],
    )
    def test_place_buy_order(self, ticker, amount_in_dollars, expected):
        """Tests TradeBot.get_stock_history_dataframe(). Test will buy $MIN_CASH_TO_RUN_TEST of AAPL stock."""

        purchase_data = self.trade_bot.place_buy_order(ticker, amount_in_dollars)
        assert (len(purchase_data) > 0) == expected

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("", 0),
            ("GOOG", 0),
            ("AAPL", MIN_CASH_TO_RUN_TEST),
        ],
    )
    def test_get_equity_in_position(self, ticker, expected):
        """Tests TradeBot.get_equity_in_position(). Due to price fluctuations, give a 1% margin of error."""

        margin_of_error = 0.01
        min_expected_value = expected * (1 - margin_of_error)
        max_expected_value = expected * (1 + margin_of_error)
        assert min_expected_value <= self.trade_bot.get_equity_in_position(ticker) <= max_expected_value

    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ("", "", False),
            ("AAPL", "", False),
            ("", 1, False),
            ("AAPL", 0.00, False),
            ("GOOG", 0, False),
            ("GOOG", 5, False),
            ("AAPL", MIN_CASH_TO_RUN_TEST + 0.01, False),
            ("AAPL", MIN_CASH_TO_RUN_TEST, TEST_MODE != _TestMode.SKIP_ALL_MARKET_ORDERS),
        ],
    )
    def test_has_sufficient_equity(self, ticker, amount_in_dollars, expected):
        """Tests TradeBot.has_sufficient_equity()."""

        assert self.trade_bot.has_sufficient_equity(ticker, amount_in_dollars) == expected

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,amount_in_dollars,expected",
        [
            ("", "", False),
            ("AAPL", "", False),
            ("", 1, False),
            ("AAPL", 0.99, False),
            ("GOOG", 5.00, False),
            ("AAPL", MIN_CASH_TO_RUN_TEST, True),
        ],
    )
    def test_place_sell_order(self, ticker, amount_in_dollars, expected):
        """
        Tests TradeBot.place_sell_order(). Sells all previously purchased AAPL stock.
        """

        sale_data = self.trade_bot.place_sell_order(ticker, amount_in_dollars)
        assert (len(sale_data) > 0) == expected

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS, _TestMode.TEST_BASIC_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize("ticker,purchase_expected", [("", False), ("MSFT", True), ("AMZN", False)])
    def test_buy_with_available_funds(self, ticker, purchase_expected):
        """Tests TradeBot.buy_with_available_funds(). Commits all available funds to a position in MSFT."""

        purchase_data = self.trade_bot.buy_with_available_funds(ticker)

        # Check there is no current cash position.
        if purchase_expected:
            assert len(purchase_data) > 0
            assert self.trade_bot.get_current_cash_position() == 0

        else:
            assert len(purchase_data) == 0

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS, _TestMode.TEST_BASIC_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "ticker,sale_expected",
        [
            ("", False),
            ("MSFT", True),
            ("MSFT", False),
        ],
    )
    def test_sell_entire_position(self, ticker, sale_expected):
        """Tests TradeBot.sell_entire_position(). Completely sell out of the position in MSFT."""

        sale_data = self.trade_bot.sell_entire_position(ticker)

        # Check that the position no longer exists in the portfolio
        if sale_expected:
            assert len(sale_data) > 0
            assert ticker not in self.trade_bot.get_current_positions()

        else:
            assert len(sale_data) == 0

    @pytest.mark.skipif(
        TEST_MODE in [_TestMode.SKIP_ALL_MARKET_ORDERS, _TestMode.TEST_BASIC_MARKET_ORDERS],
        reason="Current TestMode selected will skip this test!",
    )
    @pytest.mark.skipif(not enough_funds_to_run_test, reason="Need at least $5.00 to run the test!")
    @pytest.mark.parametrize(
        "sale_expected",
        [
            True,
            False,
        ],
    )
    def test_liquidate_portfolio(self, sale_expected):
        """Sell out of all current holdings"""

        # Place two orders so the portfolio is not empty
        if len(self.trade_bot.get_current_positions()) == 0:
            self.trade_bot.place_buy_order("AAPL", MIN_CASH_TO_RUN_TEST / 3)
            self.trade_bot.place_buy_order("MSFT", MIN_CASH_TO_RUN_TEST / 3)

        compiled_sale_data = self.trade_bot.liquidate_portfolio()

        # Check that user's portfolio is empty
        if sale_expected:
            assert len(compiled_sale_data) > 0
            assert len(self.trade_bot.get_current_positions()) == 0

        else:
            assert len(compiled_sale_data) == 0

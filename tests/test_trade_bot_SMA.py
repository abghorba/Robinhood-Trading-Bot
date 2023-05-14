import pandas as pd
import pytest

from src.bots.simple_moving_average import TradeBotSimpleMovingAverage
from src.utilities import RobinhoodCredentials
from tests.configs import STOCK_HISTORY_SAMPLE


@pytest.mark.skipif(RobinhoodCredentials().empty_credentials, reason="Robinhood credentials not provided!")
class TestTradeBotSimpleMovingAverage:
    trade_bot = TradeBotSimpleMovingAverage()
    stock_history_df = pd.DataFrame(STOCK_HISTORY_SAMPLE)

    @pytest.mark.parametrize(
        "stock_history,number_of_days,expected",
        [
            (None, None, 0),
            (pd.DataFrame(), 10, 0),
            (STOCK_HISTORY_SAMPLE, 0, 0),
            (STOCK_HISTORY_SAMPLE, -1, 0),
            (STOCK_HISTORY_SAMPLE, 25, 147.13),
            (STOCK_HISTORY_SAMPLE, 100, 145.87),
            (STOCK_HISTORY_SAMPLE, 200, 137.01),
        ],
    )
    def test_calculate_simple_moving_average(self, stock_history, number_of_days, expected):
        stock_history_df = pd.DataFrame(stock_history)
        moving_average = self.trade_bot.calculate_simple_moving_average(stock_history_df, number_of_days)
        assert moving_average == expected

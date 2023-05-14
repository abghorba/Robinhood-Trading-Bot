import pandas as pd
import pytest

from src.bots.volume_weighted_average_price import TradeBotVWAP
from src.utilities import RobinhoodCredentials
from tests.configs import AAPL_STOCK_HISTORY_SAMPLE, FB_STOCK_HISTORY_SAMPLE, GOOG_STOCK_HISTORY_SAMPLE


@pytest.mark.skipif(RobinhoodCredentials().empty_credentials, reason="Robinhood credentials not provided!")
class TestTradeBotVWAP:
    trade_bot = TradeBotVWAP()

    @pytest.mark.parametrize(
        "stock_history,expected",
        [
            (None, 0),
            (pd.DataFrame(), 0),
            (AAPL_STOCK_HISTORY_SAMPLE, 150.81),
            (FB_STOCK_HISTORY_SAMPLE, 336.60),
            (GOOG_STOCK_HISTORY_SAMPLE, 2981.67),
        ],
    )
    def test_calculate_VWAP(self, stock_history, expected):
        stock_history_df = pd.DataFrame(stock_history)
        assert self.trade_bot.calculate_VWAP(stock_history_df) == expected

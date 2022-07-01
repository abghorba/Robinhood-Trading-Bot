from ast import Or
import robin_stocks as robinhood

from trading_bots.base import OrderType
from trading_bots.base import TradeBot


class TradeBotSimpleMovingAverage(TradeBot):

    def __init__(self, username, password):
        """Logs user into their Robinhood account."""
        
        super().__init__(username, password)

    def make_order_recommendation(self, ticker):
        """
        Makes a recommendation for a market order by ...

        :param ticker: A company's ticker symbol as a string
        :return: OrderType recommendation
        """

        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        #TODO - Your own algoritm here!

        # Determine the order recommendation.
        if 0:
            return OrderType.BUY_RECOMMENDATION
        elif 0:
            return OrderType.SELL_RECOMMENDATION
        else:
            return OrderType.HOLD_RECOMMENDATION
import random

from src.bots.base_trade_bot import OrderType, TradeBot

"""
Use this sample file as a "skeleton" for making a new custom TradeBot class.
"""


class TradeBotSample(TradeBot):
    def __init__(self):
        """Logs user into their Robinhood account."""

        super().__init__()

    def make_order_recommendation(self, ticker):
        """
        Makes a recommendation for a market order by ...

        :param ticker: A company's ticker symbol as a string
        :return: OrderType recommendation
        """

        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        # TODO - Your own algorithm here!
        random_choice = random.choice(
            [OrderType.BUY_RECOMMENDATION, OrderType.SELL_RECOMMENDATION, OrderType.HOLD_RECOMMENDATION]
        )

        return random_choice

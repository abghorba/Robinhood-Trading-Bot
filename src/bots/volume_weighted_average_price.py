import pandas as pd

from src.bots.base_trade_bot import OrderType, TradeBot


class TradeBotVWAP(TradeBot):
    def __init__(self):
        """Logs user into their Robinhood account."""

        super().__init__()

    def calculate_VWAP(self, stock_history_df):
        """
        Calculates the Volume-Weighted Average Price (VWAP).

        :param stock_history_df: DataFrame containing the stock's history
        :return: The calculated Volume-Weighted Average Price
        """

        if stock_history_df is None:
            print("ERROR: stock_history_df cannot be null")
            return 0

        if stock_history_df.empty:
            print("ERROR: stock_history_df cannot be empty")
            return 0

        # Typecast the columns we need.
        stock_history_df["close_price"] = pd.to_numeric(stock_history_df["close_price"], errors="coerce")
        stock_history_df["volume"] = pd.to_numeric(stock_history_df["volume"], errors="coerce")

        # Sum the volumes, and take the dot product of the volume and close_price columns.
        sum_of_volumes = stock_history_df["volume"].sum()
        dot_product = stock_history_df["volume"].dot(stock_history_df["close_price"])

        # Calculate the VWAP.
        vwap = round(dot_product / sum_of_volumes, 2)

        return vwap

    def make_order_recommendation(self, ticker):
        """
        Makes a recommendation for a market order by comparing the Volume-Weighted Average Price (VWAP) to the current
        market price.

        :param ticker: A company's ticker symbol as a string
        :return: OrderType recommendation
        """

        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        # Calculate the VWAP from the last day in 5 minute intervals.
        stock_history_df = self.get_stock_history_dataframe(ticker, interval="5minute", time_span="day")

        vwap = self.calculate_VWAP(stock_history_df)

        # Get the current market price of the stock.
        current_price = self.get_current_market_price(ticker)

        # Determine the order recommendation.
        if current_price < vwap:
            return OrderType.BUY_RECOMMENDATION

        elif current_price > vwap:
            return OrderType.SELL_RECOMMENDATION

        else:
            return OrderType.HOLD_RECOMMENDATION

from enum import Enum

import pandas as pd
import pyotp
import robin_stocks.robinhood as robinhood

from src.utilities import RobinhoodCredentials


class OrderType(Enum):
    BUY_RECOMMENDATION = 1
    SELL_RECOMMENDATION = 0
    HOLD_RECOMMENDATION = -1


class TradeBot:
    def __init__(self):
        """Logs user into their Robinhood account."""

        robinhood_credentials = RobinhoodCredentials()
        totp = None

        if robinhood_credentials.mfa_code == "":
            print(
                "WARNING: MFA code is not supplied. Multi-factor authentication will not be attempted. If your "
                "Robinhood account uses MFA to log in, this will fail and may lock you out of your accounts for "
                "some period of time."
            )

        else:
            totp = pyotp.TOTP(robinhood_credentials.mfa_code).now()

        robinhood.login(robinhood_credentials.user, robinhood_credentials.password, mfa_code=totp)

    def robinhood_logout(self):
        """Logs user out of their Robinhood account."""

        robinhood.logout()

    def get_current_positions(self):
        """Returns a dictionary of currently held positions."""

        return robinhood.account.build_holdings()

    def get_current_cash_position(self):
        """Returns the current cash position as a float."""

        return float(robinhood.profiles.load_account_profile(info="buying_power"))

    def has_sufficient_funds_available(self, amount_in_dollars):
        """
        Returns a boolean if user's account has enough buying power to execute a buy order.

        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: True if there are sufficient funds in user's account; False otherwise
        """

        if not amount_in_dollars:
            return False

        # Retrieve the available funds.
        available_funds = self.get_current_cash_position()

        return available_funds >= amount_in_dollars

    def get_current_market_price(self, ticker):
        """
        Returns the current market price of ticker

        :param ticker: A company's symbol as a string
        :return: Current market price in USD
        """

        if not ticker:
            return 0.00

        return float(robinhood.stocks.get_latest_price(ticker, includeExtendedHours=False)[0])

    def get_company_name_from_ticker(self, ticker):
        """
        Returns the company name represented by ticker.

        :param ticker: A company's ticker symbol as a string
        :return: Company name as a string
        """

        if not ticker:
            return ""

        return robinhood.stocks.get_name_by_symbol(ticker)

    def get_stock_history_dataframe(self, ticker, interval="day", time_span="year"):
        """
        Sends request to the Robinhood API to retrieve historical stock information.

        :param ticker: A company's ticker symbol as a string
        :param interval: time intervals for data points; Values are "5minute", "10minute", "hour", "day",
         or "week". Default is "day"
        :param time_span: time span for the data points: Values are "day", "week", "month", "3month", "year", or
        "5year". Default is "year"
        :return: DataFrame of stock historical information
        """
        if (
            not ticker
            or interval not in {"5minute", "10minute", "hour", "day", "week"}
            or time_span not in {"day", "week", "month", "3month", "year", "5year"}
        ):
            return pd.DataFrame()

        stock_history = robinhood.stocks.get_stock_historicals(ticker, interval=interval, span=time_span)

        return pd.DataFrame(stock_history)

    def get_equity_in_position(self, ticker):
        """
        Returns the dollar value of the equity in the position.

        :param ticker: A company's ticker symbol as a string
        :return: float
        """

        portfolio = self.get_current_positions()

        if ticker in portfolio:
            position = portfolio[ticker]
            return float(position["equity"])

        return 0

    def has_sufficient_equity(self, ticker, amount_in_dollars):
        """
        Returns a boolean if user's account has enough equity in the given position to execute a sell order.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: True if there is sufficient equity in the user's holding; False otherwise
        """

        if not amount_in_dollars or amount_in_dollars <= 0:
            return False

        equity_in_position = self.get_equity_in_position(ticker)

        return equity_in_position >= amount_in_dollars

    def place_buy_order(self, ticker, amount_in_dollars):
        """
        Places a buy order for ticker with a specified amount.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for the purchase
        :return: Dict containing information regarding the purchase of stocks, such as the order id, the state
        of order (queued, confirmed, filled, failed, canceled, etc.), the price, and the quantity.
        """

        purchase_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return purchase_data

        if amount_in_dollars < 1:
            print("ERROR: A purchase cannot be made with less than $1.00 USD.")
            return purchase_data

        # Must have enough funds for the purchase
        if self.has_sufficient_funds_available(amount_in_dollars):
            print(f"Buying ${amount_in_dollars} of {ticker}...")
            purchase_data.update(
                robinhood.orders.order_buy_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully bought ${amount_in_dollars} of {ticker}.")

        return purchase_data

    def place_sell_order(self, ticker, amount_in_dollars):
        """
        Places a sell order for ticker with a specified amount.

        :param ticker: A company's ticker symbol
        :param amount_in_dollars: The amount in USD to be used for the sale
        :return: Dict containing information regarding the sale of stocks, such as the order id, the state of order
        (queued, confirmed, filled, failed, canceled, etc.), the price, and the quantity
        """

        sale_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return sale_data

        if amount_in_dollars < 1:
            print("ERROR: A sale cannot be made with less than $1.00 USD.")
            return sale_data

        # Must have enough equity for the sale
        if self.has_sufficient_equity(ticker, amount_in_dollars):
            print(f"Selling ${amount_in_dollars} of {ticker}...")
            sale_data.update(
                robinhood.orders.order_sell_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully sold ${amount_in_dollars} of {ticker}.")

        return sale_data

    def buy_with_available_funds(self, ticker):
        """
        Buys ticker with all available funds.

        :param ticker: A company's ticker symbol as a string
        :return: Dict containing information regarding the purchase of stocks, such as the order id, the state
        of order (queued, confirmed, filled, failed, canceled, etc.), the price, and the quantity
        """

        if not ticker:
            return {}

        available_funds = self.get_current_cash_position()

        return self.place_buy_order(ticker, available_funds)

    def sell_entire_position(self, ticker):
        """
        Sells user's entire position in ticker.

        :param ticker: A company's ticker symbol as a string
        :return: Dict containing information regarding the sale of stocks, such as the order id, the state
        of order (queued, confirmed, filled, failed, canceled, etc.), the price, and the quantity
        """

        if not ticker:
            return {}

        equity_in_position = self.get_equity_in_position(ticker)

        return self.place_sell_order(ticker, equity_in_position)

    def liquidate_portfolio(self):
        """
        Completely sells all positions held.

        :return: A list of dictionaries containing information regarding the sale of each stock held in the portfolio,
        such as the order id, the state of order (queued, confirmed, filled, failed, canceled, etc.), the price, and
        the quantity for each position held.
        """

        compiled_sale_information = []
        portfolio = self.get_current_positions()

        for ticker in portfolio.keys():
            sale_information = self.sell_entire_position(ticker)
            compiled_sale_information.append(sale_information)

        return compiled_sale_information

    def make_order_recommendation(self, ticker):
        """
        Makes an order recommendation for the given ticker.

        :param ticker: A company's ticker symbol as a string
        :return: Order recommendation
        """

        return OrderType.HOLD_RECOMMENDATION

    def trade(self, ticker, amount_in_dollars):
        """
        Places buy/sell orders for fractional shares of stock.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: Dict containing information regarding the purchase/sale of stocks, such as the order id, the state of
        order (queued, confirmed, filled, failed, canceled, etc.), the price, and the quantity.
        """

        transaction_data = {}

        action = self.make_order_recommendation(ticker)

        if action == OrderType.BUY_RECOMMENDATION:
            purchase_details = self.place_buy_order(ticker, amount_in_dollars)
            transaction_data.update(purchase_details)

        elif action == OrderType.SELL_RECOMMENDATION:
            sale_details = self.place_sell_order(ticker, amount_in_dollars)
            transaction_data.update(sale_details)

        else:
            print(f"Conditions are not met for either a purchase or a sale of {ticker}.")

        return transaction_data

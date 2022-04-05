import pandas as pd
import robin_stocks.robinhood as robinhood

from enum import Enum


class OrderType(Enum):
    BUY_RECOMMENDATION = 1
    SELL_RECOMMENDATION = 0
    HOLD_RECOMMENDATION = -1

class TradeBot():

    def __init__(self, username, password):
        """Logs user into their Robinhood account."""
        
        robinhood.login(username, password)

    def robinhood_logout(self):
        """Logs user out of their Robinhood account."""

        return robinhood.logout()

    def get_stock_history_dataframe(self, ticker, interval="day", time_span="year"):
        """
        Sends request to the Robinhood API to retrieve historical stock
        information.

        :param ticker: A company's ticker symbol as a string
        :param interval: time intervals for data points; Default 'day'
        :param time_span: time span for the data points: Default 'year'
        :return: DataFrame of stock historical information
        """

        stock_history = robinhood.stocks.get_stock_historicals(
            ticker,
            interval=interval,
            span=time_span
        )

        return pd.DataFrame(stock_history)
    
    def has_sufficient_funds_available(self, amount_in_dollars):
        """
        Returns a boolean if user's account has enough buying
        power to execute a buy order.

        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: True if there are sufficient funds in user's account; False otherwise
        """

        if not amount_in_dollars:
            return False

        # Retrieve the available funds.
        available_funds = float(
            robinhood.profiles.load_account_profile(info="buying_power")
        )

        return available_funds >= amount_in_dollars

    def has_sufficient_equity(self, ticker, amount_in_dollars):
        """
        Returns a boolean if user's account has enough equity in
        the given position to execute a sell order.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: True if there is sufficient equity in the user's holding; False otherwise
        """

        if not amount_in_dollars or amount_in_dollars <= 0:
            return False

        portfolio = robinhood.account.build_holdings()

        if ticker in portfolio:
            position = portfolio[ticker]
            equity_in_position = float(position["equity"])

            return equity_in_position >= amount_in_dollars

        return False

    def place_buy_order(self, ticker, amount_in_dollars):
        """
        Places a buy order for ticker with a specified amount.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for the purchase
        :return: Dict containaing information regarding the
        purchase of stocks, such as the order id, the state
        of order (queued, confired, filled, failed, canceled,
        etc.), the price, and the quantity.
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
        :return: Dict containing information regarding the
        sale of stocks, such as the order id, the state
        of order (queued, confired, filled, failed, canceled,
        etc.), the price, and the quantity
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
        :return: Dict containing information regarding the
        purchase of stocks, such as the order id, the state
        of order (queued, confired, filled, failed, canceled,
        etc.), the price, and the quantity
        """

        if not ticker:
            return {}

        available_funds = float(
            robinhood.profiles.load_account_profile(info="buying_power")
        )

        return self.place_buy_order(ticker, available_funds)

    def sell_entire_position(self, ticker):
        """
        Sells user's entire position in ticker.

        :param ticker: A company's ticker symbol as a string
        :return: Dict containing information regarding the
        sale of stocks, such as the order id, the state
        of order (queued, confired, filled, failed, canceled,
        etc.), the price, and the quantity
        """

        portfolio = robinhood.account.build_holdings()

        if ticker in portfolio:
            position = portfolio[ticker]
            equity = float(position["equity"])

            return self.place_sell_order(ticker, equity)

        return {}

    def liquidate_portfolio(self):
        """
        Completely sells all positions held.

        :return: A list of dictionaries containing information
        regarding the sale of each stock held in the portfolio,
        such as the order id, the state of order (queued, confired,
        filled, failed, canceled, etc.), the price, and the quantity
        for each position held.
        """

        compiled_sale_information = []
        portfolio = robinhood.account.build_holdings()

        for ticker in portfolio.keys():
            sale_information = self.sell_entire_position(ticker)
            compiled_sale_information.append(sale_information)

        return compiled_sale_information

    def make_order_recommendation(self, ticker):
        """Makes an order recommendation for the given ticker.

        :param ticker: A company's ticker symbol as a string
        :return: Order recommendation
        """

        return OrderType.HOLD_RECOMMENDATION

    def trade(self, ticker, amount_in_dollars):
        """
        Places buy/sell orders for fractional shares of stock.

        :param ticker: A company's ticker symbol as a string
        :param amount_in_dollars: The amount in USD to be used for a transaction
        :return: Dict containing information regarding the
        purchase/sale of stocks, such as the order id, the
        state of order (queued, confired, filled, failed,
        canceled, etc.), the price, and the quantity.
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
            print(
                f"Conditions are not met for either a purchase or a sale of {ticker}."
            )

        return transaction_data

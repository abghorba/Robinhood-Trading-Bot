import robin_stocks.robinhood as robinhood

import os
import time
import trade_bot

def main():
    robin_user = os.environ.get("robinhood_username")
    robin_pass = os.environ.get("robinhood_password")

    robinhood.login(username=robin_user,
                    password=robin_pass,
                    expiresIn=86400,
                    by_sms=True)

    """
    Returns a dictionary where the keys are the stock tickers and 
    the value is another dictionary that has the stock price, 
    quantity held, equity, percent change, equity change, type, 
    name, id, pe ratio, percentage of portfolio, and average buy price.
    """
    # current_holdings = robinhood.build_holdings()
    # print(current_holdings)

    stock_trade_list = ['AMZN', 'AAPL', 'MSFT', 'FB', 'GOOG', 'TSLA', 'ENPH', 'NIO', 'TDOC']
    stock_bot = trade_bot.TradeBot(stock_trade_list)
    for ticker in stock_trade_list:
        print(ticker)
        print(stock_bot.make_order_recommendation(ticker))

    # crypto_trade_list = ['DOGE', 'ETH', 'BTC', 'ADA']
    # crypto_bot = trade_bot.TradeBotCrypto(crypto_trade_list)
    # for ticker in crypto_trade_list:
    #     print(ticker)
    #     print(crypto_bot.make_order_recommendation(ticker))

    # stock_trade_list = ['AMZN', 'AAPL', 'MSFT', 'FB', 'GOOG', 'TSLA', 'ENPH', 'NIO', 'TDOC']
    # stock_bot = trade_bot.TradeBotVWAP(stock_trade_list)
    # for ticker in stock_trade_list:
    #     print(ticker)
    #     print(stock_bot.make_order_recommendation(ticker))

if __name__ == "__main__":
    main()
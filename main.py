import robin_stocks.robinhood as robinhood

import os
import trade_bot

def trade_stock_bot(trade_list, algorithm_type):
    if algorithm_type == 1:
        crypto_bot = trade_bot.TradeBot(trade_list)
    elif algorithm_type == 2:
        crypto_bot = trade_bot.TradeBotVWAP(trade_list)
    elif algorithm_type == 3:
        crypto_bot = trade_bot.TradeBotPairsTrading(trade_list)
    elif algorithm_type == 4:
        crypto_bot = trade_bot.TradeBotSentimentAnalysis(trade_list)
    else:
        raise Exception('Invalid algorithm type.')
        
    for ticker in trade_list:
        print(ticker, stock_bot.make_order_recommendation(ticker))
    stock_bot.trade()

def trade_crypto_bot(trade_list, algorithm_type):
    if algorithm_type == 1:
        crypto_bot = trade_bot.TradeBotCrypto(trade_list)
    elif algorithm_type == 2:
        crypto_bot = trade_bot.TradeBotCryptoVWAP(trade_list)
    elif algorithm_type == 3:
        crypto_bot = trade_bot.TradeBotCryptoPairsTrading(trade_list)
    elif algorithm_type == 4:
        crypto_bot = trade_bot.TradeBotCryptoSentimentAnalysis(trade_list)
    else:
        raise Exception('Invalid algorithm type.')

    for ticker in trade_list:
        print(ticker, crypto_bot.make_order_recommendation(ticker))
    crypto_bot.trade()

def main():
    robin_user = os.environ.get("robinhood_username")
    robin_pass = os.environ.get("robinhood_password")

    robinhood.login(username=robin_user,
                    password=robin_pass,
                    expiresIn=86400,
                    by_sms=True)

    stock_trade_list = ['AAPL', 'ENPH']
    crypto_trade_list = ['BTC', 'DOGE']

    my_holdings = robinhood.account.build_holdings()
    my_holding_in_ticker = my_holdings['AMZN']
    quantity_in_ticker = my_holding_in_ticker['quantity']
    order = robinhood.orders.order_sell_fractional_by_quantity('AMZN', quantity_in_ticker)
    print(order)

if __name__ == "__main__":
    main()
import sys

from src.bots.base_trade_bot import TradeBot
from src.bots.simple_moving_average import TradeBotSimpleMovingAverage
from src.bots.twitter_sentiments import TradeBotTwitterSentiments
from src.bots.volume_weighted_average_price import TradeBotVWAP


def main():
    if len(sys.argv) != 2:
        raise Exception("ERROR: Usage: python sample.py <company_ticker>")

    args = sys.argv[1:]
    ticker = args[0]

    tb0 = TradeBot()
    tb1 = TradeBotSimpleMovingAverage()
    tb2 = TradeBotVWAP()
    tb3 = TradeBotTwitterSentiments()

    print(f"Current positions : {tb0.get_current_positions()}")
    print(f"Current cash position : ${tb0.get_current_cash_position()}")
    print(f"Market price of {tb0.get_company_name_from_ticker(ticker)} is ${tb0.get_current_market_price(ticker)}")
    print(f"SimpleMovingAverage : {tb1.make_order_recommendation(ticker)}")
    print(f"VWAP : {tb2.make_order_recommendation(ticker)}")
    print(f"TwitterSentiments : {tb3.make_order_recommendation(ticker)}")


if __name__ == "__main__":
    main()

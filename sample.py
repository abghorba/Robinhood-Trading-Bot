import sys

from config import ROBINHOOD_USER, ROBINHOOD_PASS
from trading_bots.base import TradeBot
from trading_bots.simple_moving_average import TradeBotSimpleMovingAverage
from trading_bots.volume_weighted_average_price import TradeBotVWAP
from trading_bots.twitter_sentiments import TradeBotSentimentAnalysis


# Usage: python sample.py <company_ticker>

def main():

    if len(sys.argv) != 2:
        raise Exception
        
    args = sys.argv[1:]
    ticker = args[0]

    tb0 = TradeBot(ROBINHOOD_USER, ROBINHOOD_PASS)
    tb1 = TradeBotSimpleMovingAverage(ROBINHOOD_USER, ROBINHOOD_PASS)
    tb2 = TradeBotVWAP(ROBINHOOD_USER, ROBINHOOD_PASS)
    tb3 = TradeBotSentimentAnalysis(ROBINHOOD_USER, ROBINHOOD_PASS)

    print(f"Current positions : {tb0.get_current_positions()}")
    print(f"Current cash position : {tb0.get_current_cash_position()}")

    company_name = tb0.get_company_name_from_ticker(ticker)
    print(f"Market price of {company_name} is ${tb0.get_current_market_price(ticker)}")

    # Order Recommendations from the bots
    print(f"SimpleMovingAverage : {tb1.make_order_recommendation(ticker)}")
    print(f"VWAP : {tb2.make_order_recommendation(ticker)}")
    print(f"TwitterSentiment : {tb3.make_order_recommendation(ticker)}")

if __name__ == "__main__":
    main()

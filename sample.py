from src.bots.simple_moving_average import TradeBotSimpleMovingAverage


def main():
    tb = TradeBotSimpleMovingAverage()

    print(f"Current positions : {tb.get_current_positions()}")
    print(f"Current cash position : ${tb.get_current_cash_position()}")
    print(f"Market price of {tb.get_company_name_from_ticker('AAPL')} is ${tb.get_current_market_price('AAPL')}")
    print(f"SimpleMovingAverage : {tb.make_order_recommendation('AAPL')}")

    # tb.trade(ticker='AAPL', amount_in_dollars=5.00)


if __name__ == "__main__":
    main()

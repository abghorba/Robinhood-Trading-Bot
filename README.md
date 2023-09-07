# Robinhood Trading Bot
A Python trading bot that uses Robinhood to execute market orders based on various trading algorithms.

<h2> Setting Up </h2>
You will need to have a Robinhood account. It is optional to have Twitter API keys (you won't be able to use the
Twitter Sentiment trading bot, however).

It is up to you to decide if you want Multi-Factor Authentication (MFA) enabled on your Robinhood account.
To set up MFA, log into your Robinhood account and navigate to Menu > Security and privacy > Two-Factor Authentication.
Choose "Authenticator App" as your form of MFA. You can use Duo Mobile, Google Authenticator, whatever you like. Copy the
key that Robinhood provides you. This is the MFA token you need in order to generate a time-based one-time password (TOTP).
Use this in any authenticator app of your choice to enable it. This key will also be used below in the ROBINHOOD_MFA_CODE variable.

Navigate to initialize.sh and populate the following:

        TWITTER_CONSUMER_KEY=""
        TWITTER_CONSUMER_SECRET=""
        ROBINHOOD_USER=""
        ROBINHOOD_PASS=""
        ROBINHOOD_MFA_CODE=""

After this is done, you can create a virtual environment, install dependencies, and create your .env file by running:

        sh initialize.sh

We are now ready for usage!!


<h2> Usage </h2>
You can choose which algorithm you want to trade with or create your own bot with your own algorithm.

<h3> Using Existing TradeBots </h3>
To use one of the existing TradeBots, you will need to create a new Python file in the project's root directory. Import
the TradeBot you wish to use. For example, let's use TradeBotSimpleMovingAverage. Your script would look something like
this:

        from src.bots.simple_moving_average import TradeBotSimpleMovingAverage

        trade_bot = TradeBotSimpleMovingAverage()
        trade_bot.trade(ticker="AAPL", amount_in_dollars=5.00)

This will initialize the TradeBot that uses the Simple Moving Average algorithm and will attempt a trade for $5.00 of 
Apple stock.

What type of trade will this bot do? In this case, it depends on the values of the 50-day and 200-day moving averages.
We're letting the algorithm decide whether to buy, sell, or do nothing.

<h3> Creating a Custom TradeBot </h3>
Take a look at the file new_bot_sample.py for an example. The only function you will need to modify to get this to work 
is:

        make_order_recommendation(self, ticker)

Let's say we want to create a new TradeBot, call it TradeBotSample. We should create a new module in src/bots/ containing
the code for the new TradeBotSample object. This new object should inherit from the base TradeBot in base_trade_bot.py. 
Then we can override the make_order_recommendation() function to use our new algorithm. Add in whatever helper functions 
you may need. Make sure that the make_order_recommendation() function returns a value of type OrderType!

Then, we can create a new Python file in the project's root directory with the following:

        from src.bots.random import TradeBotSample

        trade_bot = TradeBotSample()
        trade_bot.trade(ticker="AAPL", amount_in_dollars=5.00)

The trade() function will buy, sell, or do nothing depending on how we implement the make_order_recommendation()
function.

If your new TradeBot contains a useful algorithm that is not already included, please open a Pull Request to add in your
new TradeBot!


<h2> Sample Algorithm Explanations </h2>

<h3> Moving Day Average Comparison </h3>
First, the 50-day and 200-day moving averages are calculated using historical stock prices. 
A buy order recommendation is made when the 50-day moving average is strictly greater than the 200-day moving average.
A sell order recommendation is made when the 50-day moving average is strictly less than the 200-day moving average.
No recommendation is made when the two moving averages are equal.

<h3> Volume-Weighted Average Price Comparison </h3>
The Volume-Weighted Average Price (VWAP) is calculated by adding up the dollars traded for every transaction in a period (price times number of shares traded)
and then dividing by the total shares traded in the period. When the current price of a security is below the VWAP, a buy recommendation is made.
A sell recommendation is made when the current price of a security is above the VWAP. If neither conditions are met, no recommendation is made.

<h3> Sentiment Analysis </h3>
This algorithm sources tweets from the Twitter API that mention a company's name. A sentiment analysis is performed on each tweet and a score is assigned
which details the negativity, neutrality, or positivity of the sentiment. The average sentiment score is taken and if the sentiment is positive a buy
order recommendation is made, if the sentiment is negative a sell order recommendation is made, and if the sentiment is neutral no order recommendation
is made.


<h2> Disclaimer </h2>
Any stock or ticker mentioned is not to be taken as financial advice. You are using this bot at your own discretion and with the knowledge that you can lose
(part of) your investment.

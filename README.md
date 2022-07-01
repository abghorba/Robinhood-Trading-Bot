# Robinhood Trading Bot
A Python trading bot that uses Robinhood to execute market orders based on various trading algorithms.

<h2> Algorithm Explanations </h2>

<h3> Moving Day Average Comparison </h3>
First, the 50-day and 200-day moving averages are calculated using historical stock prices. 
A buy order recommendation is made when the 50-day moving average is strictly greater than the 200-day moving average.
A sell order recommendation is made when the 50-day moving average is strictly less than the 200-day moving average.
No recommendation is amde when the two moving averages are equal.

<h3> Volume-Weighted Average Price Comparison </h3>
The Volume-Weighted Average Price (VWAP) is calculated by adding up the dollars traded for every transaction in a period (price times number of shares traded)
and then dividing by the total shares traded in the period. When the current price of a security is below the VWAP, a buy recommendation is made.
A sell recommendation is made when the currentprice of a security is above the VWAP. If neither conditions are met, no recommendation is made.

<h3> Sentiment Analysis </h3>
This algorithm sources tweets from the Twitter API that mention a company's name. A sentiment analysis is performed on each tweet and a score is assigned
which details the negativity, neutrality, or positivity of the sentiment. The average sentiment score is taken and if the sentiment is positive a buy
order recommendation is made, if the sentiment is negative a sell order recommendation is made, and if the sentiment is neutral no order recommendation
is made.


<h2> Setting Up </h2>
You will need to have a Robinhood account and a Twitter API key. Navigate to initialize.sh and populate the following:

        TWITTER_CONSUMER_KEY=""
        TWITTER_CONSUMER_SECRET=""
        ROBINHOOD_USER=""
        ROBINHOOD_PASS=""

After this is done, you can create a virtual environment, install dependencies, and create your .env file by running:

        sh initialize.sh

We are now ready for usage!!


<h2> Usage </h2>
You can choose which algorithm you want to trade with. Then call the function

        trade(ticker, amount_in_dollars)

and your bot will trade ticker with the specified amount_in_dollars.

If you want to create your own bot with your own algorithm, you simply need to navigate to new_bot_skeleton.py found in the trading_bots folder and add
your own algorithm into:
        
        make_order_recommendation(self, ticker):

Add in whatever helper functions you may need. Make sure that the above function returns a value of type OrderType!

Have fun!

<h2> Disclaimer </h2>
Any stock or ticker mentioned is not to be taken as financial advice. You are using this bot at your own discretion and with the knowledge that you can lose
(part of) your investment.

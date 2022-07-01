import os

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

ROBINHOOD_USER = os.getenv('ROBINHOOD_USER')
ROBINHOOD_PASS = os.getenv('ROBINHOOD_PASS')

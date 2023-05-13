import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TwitterAuth:
    def __init__(self):
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")


class RobinhoodAuth:
    def __init__(self):
        self.user = os.getenv("ROBINHOOD_USER")
        self.password = os.getenv("ROBINHOOD_PASS")
        self.mfa_code = os.getenv("ROBINHOOD_MFA_CODE")

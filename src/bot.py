import tweepy
from generator import QuoteGenerator
import os
import dotenv
import time

dotenv.load_dotenv()


class TwitterBot(tweepy.Client):
    def __init__(self):
        auth = {
            "bearer_token": os.getenv("BEARER_TOKEN"),
            "access_token": os.getenv("ACCESS_TOKEN"),
            "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET"),
            "consumer_key": os.getenv("CONSUMER_KEY"),
            "consumer_secret": os.getenv("CONSUMER_SECRET")
        }
        super().__init__(**auth)
        self.generator = QuoteGenerator
        del auth["bearer_token"]
        self.api = tweepy.API(auth=tweepy.OAuthHandler(**auth))

    def start(self):
        print("Starting bot...")
        while True:
            print("Generating quote...")
            quote = self.generator.generate_quote()

            file = self.api.media_upload(quote.path)

            self.create_tweet(
                media_ids=[file.media_id],
            )

            print("Posted tweet.")

            time.sleep(3600)


if __name__ == "__main__":
    bot = TwitterBot()
    bot.start()

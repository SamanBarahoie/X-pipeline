import json
import time
import tweepy
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
import os

#~~~~~~~~~~~~~ Setup Logging ~~~~~~~~~~~~~#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

#~~~~~~~~~~~~~ Load Twitter Credentials ~~~~~~~~~~~~~#
try:
    with open('twitter_credentials.json') as f:
        creds = json.load(f)
    logger.info("Credentials file loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load twitter_credentials.json: {e}")
    raise

try:
    BEARER_TOKEN = creds['BEARER_TOKEN']
    logger.info(f"Credentials loaded: BEARER_TOKEN len={len(BEARER_TOKEN)}")
except KeyError as e:
    logger.error(f"Missing credential in twitter_credentials.json: {e}")
    raise

#~~~~~~~~~~~~~ Authenticate with Twitter API v2 ~~~~~~~~~~~~~#
try:
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    logger.info("Tweepy v2 Client initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Tweepy v2 Client: {e}")
    raise

#~~~~~~~~~~~~~ Log System Time ~~~~~~~~~~~~~#
logger.info(f"Current system time: {time.ctime()}")

#~~~~~~~~~~~~~ Test Twitter API Authentication ~~~~~~~~~~~~~#
def test_auth():
    """
    Test authentication with the Twitter API v2 by making a simple request.
    """
    try:
        response = client.get_me()
        logger.info(f"Twitter API v2 authentication successful. Connected as @{response.data.username}")
    except Exception as e:
        logger.error(f"Twitter API v2 authentication failed: {e}")

# Call test_auth to verify authentication
#test_auth()

#~~~~~~~~~~~~~ Create Kafka Producer with Retry Logic ~~~~~~~~~~~~~#
def create_kafka_producer():
    """
    Retry connecting to Kafka producer until successful.
    """
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5
            )
            logger.info("Kafka Producer connected.")
            return producer
        except KafkaError as e:
            logger.error(f"Kafka connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

producer = create_kafka_producer()

#~~~~~~~~~~~~~ Fetch Tweets from Twitter ~~~~~~~~~~~~~#
def fetch_tweets(keyword, count=10):
    """
    Search for recent tweets containing a specific keyword using Twitter API v2.
    Returns a list of tweet dicts.
    """
    try:
        response = client.search_recent_tweets(
            query=f"{keyword} lang:en",  # Filter for English tweets
            max_results=count,
            tweet_fields=['created_at'],
            expansions=['author_id'],
            user_fields=['username']
        )
        if response.data:
            users = {u.id: u.username for u in response.includes.get('users', [])}
            return [{
                'id': str(tweet.id),
                'text': tweet.text,
                'created_at': str(tweet.created_at),
                'user': users.get(tweet.author_id, 'N/A')
            } for tweet in response.data]
        else:
            logger.warning("No tweets found for query.")
            return []
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return []

#~~~~~~~~~~~~~ Main Loop to Produce Tweets to Kafka ~~~~~~~~~~~~~#
def main():
    global producer
    keyword = "news"
    while True:
        tweets = fetch_tweets(keyword,count=44)
        if tweets:
            for tweet in tweets:
                try:
                    producer.send('twitter_topic', value=tweet)
                    logger.info(f"Produced tweet: {tweet['id']}")
                except KafkaError as e:
                    logger.error(f"Error sending to Kafka: {e}. Recreating producer...")
                    producer = create_kafka_producer()
        else:
            logger.warning("No tweets fetched.")

        #~~~~~~~~~~~~~ Wait before next fetch to respect rate limits ~~~~~~~~~~~~~#
        time.sleep(300)

if __name__ == "__main__":
    main()
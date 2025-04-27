import json
import time
import psycopg2
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging

#~~~~~~~~~~~~ Setup Logging ~~~~~~~~~~~~#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

#~~~~~~~~~~~~ Connect to PostgreSQL with Retry ~~~~~~~~~~~~#
def connect_postgres():
    """
    Retry connecting to PostgreSQL until successful.
    """
    while True:
        try:
            conn = psycopg2.connect(
                host='postgres',  # use 'localhost' if not in Docker
                port='5432',
                database='twitter_etl',
                user='twitter',
                password='twitterpass'
            )
            logger.info("PostgreSQL connection established.")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"PostgreSQL connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Initialize Postgres connection and cursor
conn = connect_postgres()
cursor = conn.cursor()

#~~~~~~~~~~~~ Ensure tweets table exists ~~~~~~~~~~~~#
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id TEXT PRIMARY KEY,
        text TEXT,
        created_at TIMESTAMP,
        username TEXT
    )
''')
conn.commit()
logger.info("Ensured tweets table exists in PostgreSQL.")

#~~~~~~~~~~~~ Create Kafka Consumer with Retry ~~~~~~~~~~~~#
def create_consumer():
    """
    Retry connecting to Kafka consumer until successful.
    """
    while True:
        try:
            consumer = KafkaConsumer(
                'twitter_topic',
                bootstrap_servers=['kafka:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='twitter_etl_group'
            )
            logger.info("Kafka Consumer connected and subscribed to 'twitter_topic'.")
            return consumer
        except KafkaError as e:
            logger.error(f"Kafka connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

consumer = create_consumer()

#~~~~~~~~~~~~ Insert Tweet into Database ~~~~~~~~~~~~#
def insert_tweet(tweet):
    """
    Insert a tweet record into the PostgreSQL tweets table.
    """
    global conn, cursor
    try:
        cursor.execute('''
            INSERT INTO tweets (id, text, created_at, username)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        ''', (
            tweet['id'],
            tweet['text'],
            tweet['created_at'],
            tweet['user']
        ))
        conn.commit()
        logger.info(f"Inserted tweet {tweet['id']} into database.")
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(f"Error inserting tweet {tweet['id']} into database: {e}")
        # Attempt to reconnect to PostgreSQL
        conn = connect_postgres()
        cursor = conn.cursor()

#~~~~~~~~~~~~ Main Loop to Consume from Kafka ~~~~~~~~~~~~#
def main():
    """
    Continuously consume messages from Kafka and process them.
    """
    global consumer
    while True:
        try:
            for message in consumer:
                tweet = message.value
                logger.info(f"Consumed tweet: {tweet['id']}")
                insert_tweet(tweet)
        except KafkaError as e:
            logger.error(f"Kafka error while consuming: {e}. Recreating consumer...")
            consumer = create_consumer()

if __name__ == "__main__":
    main()

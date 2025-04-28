
  
    

  create  table "twitter_etl"."public"."mart_tweet_count_per_hour__dbt_tmp"
  
  
    as
  
  (
    

WITH tweet_counts AS (
    SELECT
        DATE_TRUNC('hour', created_at) AS tweet_hour,
        COUNT(*) AS tweet_count
    FROM "twitter_etl"."public"."stg_twitter_data"
    WHERE cleaned_text IS NOT NULL
    GROUP BY 1
)

SELECT
    tweet_hour,
    tweet_count
FROM tweet_counts
-- ORDER BY tweet_hour;  -- deleted
  );
  
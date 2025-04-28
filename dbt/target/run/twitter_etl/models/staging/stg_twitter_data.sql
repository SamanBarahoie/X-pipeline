
  
    

  create  table "twitter_etl"."public"."stg_twitter_data__dbt_tmp"
  
  
    as
  
  (
    WITH cleaned_tweets AS (
    SELECT
        id,
        TRIM(BOTH FROM text) AS text, -- Remove leading and trailing spaces
        CAST(created_at AS TIMESTAMP) AS created_at, -- Standardize date format
        username,  -- Directly use username as it's a simple string
        LENGTH(TRIM(BOTH FROM text)) AS text_length,  -- Length of the tweet text
        EXTRACT(DOW FROM CAST(created_at AS TIMESTAMP)) AS day_of_week,  -- Extract day of the week (0=Sunday, 6=Saturday)
        REGEXP_REPLACE(
            text,
            '((https?://[^\s]+)|(#[^\s]+)|(@[^\s]+))',
            '',
            'g'
        ) AS cleaned_text, -- Remove links, hashtags, and mentions from the text
        CASE
            WHEN text ~ '^(https?://|www\.)' THEN FALSE
            ELSE TRUE
        END AS is_not_only_url  -- Check if the text is not just a URL
    FROM "twitter_etl"."public"."tweets"
    WHERE
        text IS NOT NULL -- Exclude tweets without text
        AND created_at IS NOT NULL -- Exclude tweets without date
        AND LENGTH(TRIM(BOTH FROM text)) > 3 -- Exclude very short tweets
)

SELECT
    id,
    text AS original_text,
    cleaned_text,
    created_at,
    username,  -- Directly use username
    text_length,
    day_of_week,
    is_not_only_url
FROM cleaned_tweets
WHERE
    is_not_only_url = TRUE -- Only include tweets that are not just URLs
    AND cleaned_text <> '' -- Ensure the cleaned text is not empty
  );
  

CREATE TABLE IF NOT EXISTS timeline_tweets (
  id BIGSERIAL PRIMARY KEY,
  tweet_id VARCHAR(50) NOT NULL UNIQUE,
  content TEXT NOT NULL,
  author VARCHAR(50),
  tweet_url TEXT,
  thread_selected BOOLEAN DEFAULT false,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_timeline_tweets_tweet_id ON timeline_tweets(tweet_id);

CREATE INDEX IF NOT EXISTS idx_timeline_tweets_author ON timeline_tweets(author);

CREATE INDEX IF NOT EXISTS idx_timeline_tweets_scraped_at ON timeline_tweets(scraped_at DESC);


ALTER TABLE timeline_tweets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role"
  ON timeline_tweets
  FOR ALL
  TO authenticated, anon
  USING (true)
  WITH CHECK (true);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_timeline_tweets_updated_at
  BEFORE UPDATE ON timeline_tweets
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE VIEW recent_timeline_tweets AS
SELECT 
  tweet_id,
  author,
  LEFT(content, 100) as content_preview,
  tweet_url,
  scraped_at
FROM timeline_tweets
ORDER BY scraped_at DESC
LIMIT 50;

CREATE OR REPLACE VIEW tweets_by_author AS
SELECT 
  author,
  COUNT(*) as tweet_count,
  MAX(scraped_at) as last_scraped_at
FROM timeline_tweets
WHERE author IS NOT NULL
GROUP BY author
ORDER BY tweet_count DESC;

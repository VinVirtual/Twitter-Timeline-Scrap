import os
import time
import random
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Browser, Page
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TwitterScraperPlaywright:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.context = None
        self.playwright = None
        self.supabase: Client = None
        self.init_supabase()
    
    def init_supabase(self):
        """Initialize Supabase client"""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                raise Exception("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client initialized")
            
            # Test connection
            self.test_connection()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            raise
    
    def test_connection(self):
        """Test Supabase connection"""
        try:
            response = self.supabase.table('timeline_tweets').select('id', count='exact').limit(1).execute()
            logger.info("✅ Supabase connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection test failed: {e}")
            raise
    
    def is_duplicate(self, tweet_id):
        """Check if tweet already exists in database"""
        try:
            response = self.supabase.table('timeline_tweets').select('id').eq('tweet_id', tweet_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"❌ Error checking duplicate for {tweet_id}: {e}")
            return False
    
    def save_tweet(self, tweet_id, content, author, tweet_url):
        """Save tweet to Supabase if not duplicate"""
        if self.is_duplicate(tweet_id):
            logger.info(f"⏭️  Skipping duplicate tweet: {tweet_id}")
            return False
        
        try:
            data = {
                'tweet_id': tweet_id,
                'content': content,
                'author': author,
                'tweet_url': tweet_url
            }
            
            response = self.supabase.table('timeline_tweets').insert(data).execute()
            
            logger.info(f"✅ Saved new tweet: {tweet_id} by @{author}")
            return True
            
        except Exception as e:
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                logger.warning(f"⚠️  Tweet {tweet_id} already exists (caught by unique constraint)")
                return False
            else:
                logger.error(f"❌ Error saving tweet {tweet_id}: {e}")
                return False
    
    def setup_browser(self):
        """Initialize Playwright browser with anti-detection measures"""
        try:
            logger.info("=" * 60)
            logger.info("STEP 1: Setting up Playwright browser")
            logger.info("=" * 60)
            logger.info("🔧 Setting up Playwright with anti-bot detection...")
            
            # Create a separate profile directory for scraping
            import tempfile
            scraper_profile = os.path.join(tempfile.gettempdir(), "twitter-scraper-profile")
            os.makedirs(scraper_profile, exist_ok=True)
            
            logger.info(f"📁 Using scraper profile: {scraper_profile}")
            
            self.playwright = sync_playwright().start()
            
            # Launch browser with dedicated scraper profile
            logger.info("🌐 Launching browser...")
            self.context = self.playwright.chromium.launch_persistent_context(
                scraper_profile,
                headless=False,  # Set to True for headless mode
                channel="chrome",  # Use installed Chrome
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ],
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
            )
            
            # Get the first page (tab)
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
            
            logger.info("✅ Browser opened successfully")
            
            # Remove webdriver property
            logger.info("🔧 Applying anti-detection script...")
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            logger.info("✅ Anti-detection applied")
            
            logger.info("✅ Playwright browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            raise
    
    def extract_tweet_id_from_url(self, url):
        """Extract tweet ID from Twitter URL"""
        try:
            if '/status/' in url:
                tweet_id = url.split('/status/')[-1].split('?')[0].split('/')[0]
                return tweet_id
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting tweet ID from {url}: {e}")
            return None
    
    def extract_author_from_url(self, url):
        """Extract author username from Twitter URL"""
        try:
            if '/status/' in url:
                parts = url.split('/')
                username_index = parts.index('x.com') + 1 if 'x.com' in parts else parts.index('twitter.com') + 1
                return parts[username_index]
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting author from {url}: {e}")
            return None
    
    def collect_tweets(self, max_tweets=10):
        """Collect tweets from timeline"""
        if not self.page:
            raise Exception("Browser not initialized")
        
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Collecting tweets from timeline")
        logger.info("=" * 60)
        logger.info(f"🚀 Starting tweet collection (max: {max_tweets})...")
        
        # Navigate to Twitter home timeline
        logger.info("🌐 Navigating to https://x.com/home ...")
        try:
            self.page.goto("https://x.com/home", wait_until="load", timeout=60000)  # 60 second timeout
            logger.info("✅ Page navigation completed")
        except Exception as e:
            logger.warning(f"⚠️  Navigation timeout (expected on first run): {e}")
            logger.info("✅ Continuing anyway...")
        
        # Random wait time for page to fully load
        wait_time = random.uniform(5, 8)
        logger.info(f"⏳ Waiting {wait_time:.1f} seconds for content to load...")
        time.sleep(wait_time)
        
        # Check if we need to login
        current_url = self.page.url
        if 'login' in current_url or 'signin' in current_url:
            logger.warning("⚠️  You need to log into Twitter!")
            logger.info("🔑 Please log in manually in the browser window...")
            logger.info("⏳ Waiting 60 seconds for you to log in...")
            time.sleep(60)
            logger.info("✅ Continuing with scraping...")
        else:
            logger.info("✅ Already logged in, starting to collect tweets...")
        
        tweets_data = []
        processed_tweet_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 20
        
        while len(tweets_data) < max_tweets and scroll_attempts < max_scroll_attempts:
            # Find all tweet elements
            tweet_elements = self.page.query_selector_all('article[role="article"]')
            
            logger.info(f"📊 Found {len(tweet_elements)} tweet elements on page (attempt {scroll_attempts + 1}/{max_scroll_attempts})")
            
            for tweet_element in tweet_elements:
                if len(tweets_data) >= max_tweets:
                    break
                
                try:
                    # Find the link to the tweet
                    tweet_link = tweet_element.query_selector('a[href*="/status/"]')
                    if not tweet_link:
                        continue
                    
                    tweet_url = tweet_link.get_attribute('href')
                    if not tweet_url.startswith('http'):
                        tweet_url = f"https://x.com{tweet_url}"
                    
                    # Extract tweet ID
                    tweet_id = self.extract_tweet_id_from_url(tweet_url)
                    
                    if not tweet_id:
                        logger.debug("⚠️  Could not extract tweet ID, skipping")
                        continue
                    
                    # Skip if already processed
                    if tweet_id in processed_tweet_ids:
                        logger.debug(f"⏭️  Tweet {tweet_id} already processed in this session")
                        continue
                    
                    processed_tweet_ids.add(tweet_id)
                    
                    # Extract author
                    author = self.extract_author_from_url(tweet_url)
                    
                    # Extract tweet content
                    tweet_content = tweet_element.inner_text()
                    
                    # Store tweet data
                    tweet_data = {
                        'tweet_id': tweet_id,
                        'content': tweet_content,
                        'author': author,
                        'url': tweet_url
                    }
                    
                    tweets_data.append(tweet_data)
                    logger.info(f"📥 [{len(tweets_data)}/{max_tweets}] Collected: {tweet_id} by @{author}")
                    
                    # Small random delay
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    logger.debug(f"⚠️  Error processing tweet element: {e}")
                    continue
            
            # Scroll down to load more tweets (human-like behavior)
            if len(tweets_data) < max_tweets:
                # Random scroll patterns (humans don't scroll the same amount each time)
                scroll_pattern = random.choice(['small', 'medium', 'large'])
                
                if scroll_pattern == 'small':
                    scroll_amount = random.randint(200, 400)
                elif scroll_pattern == 'medium':
                    scroll_amount = random.randint(400, 700)
                else:  # large
                    scroll_amount = random.randint(700, 1000)
                
                logger.debug(f"📜 Human-like scroll ({scroll_pattern}): {scroll_amount}px...")
                
                # Smooth scroll (more human-like than instant)
                self.page.evaluate(f"""
                    window.scrollTo({{
                        top: window.scrollY + {scroll_amount},
                        behavior: 'smooth'
                    }});
                """)
                
                # Sometimes scroll up a bit (humans do this when they miss something)
                if random.random() < 0.15:  # 15% chance
                    time.sleep(random.uniform(0.5, 1))
                    scroll_back = random.randint(50, 150)
                    logger.debug(f"👆 Scrolling back up {scroll_back}px (human behavior)...")
                    self.page.evaluate(f"window.scrollBy(0, -{scroll_back})")
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Variable wait time (humans read at different speeds)
                scroll_wait = random.uniform(2.5, 6)
                logger.debug(f"⏳ Reading tweets for {scroll_wait:.1f}s...")
                time.sleep(scroll_wait)
                scroll_attempts += 1
        
        logger.info(f"✅ Collected {len(tweets_data)} tweets")
        return tweets_data
    
    def scrape_and_save(self, max_tweets=10):
        """Main function: Scrape tweets and save to Supabase"""
        try:
            # Setup browser
            self.setup_browser()
            
            # Collect tweets
            tweets = self.collect_tweets(max_tweets)
            
            # Save to Supabase
            logger.info(f"\n💾 Saving tweets to Supabase...")
            saved_count = 0
            skipped_count = 0
            
            for i, tweet in enumerate(tweets, 1):
                logger.debug(f"💾 [{i}/{len(tweets)}] Processing tweet {tweet['tweet_id']}...")
                success = self.save_tweet(
                    tweet_id=tweet['tweet_id'],
                    content=tweet['content'],
                    author=tweet['author'],
                    tweet_url=tweet['url']
                )
                
                if success:
                    saved_count += 1
                else:
                    skipped_count += 1
                
                time.sleep(random.uniform(0.1, 0.3))
            
            result = {
                "total_collected": len(tweets),
                "saved": saved_count,
                "skipped_duplicates": skipped_count,
                "tweets": tweets
            }
            
            logger.info(f"\n{'='*50}")
            logger.info(f"📊 SCRAPING SUMMARY:")
            logger.info(f"   Total Collected: {result['total_collected']}")
            logger.info(f"   ✅ Saved: {result['saved']}")
            logger.info(f"   ⏭️  Skipped (duplicates): {result['skipped_duplicates']}")
            logger.info(f"{'='*50}\n")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            raise
        finally:
            if self.context:
                self.context.close()
                logger.info("🔒 Browser closed")
            if self.playwright:
                self.playwright.stop()
    
    def get_all_tweets(self, limit=100):
        """Retrieve tweets from Supabase"""
        try:
            response = self.supabase.table('timeline_tweets')\
                .select('*')\
                .order('scraped_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"❌ Error fetching tweets: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            # Total tweets
            total_response = self.supabase.table('timeline_tweets')\
                .select('id', count='exact')\
                .execute()
            total = total_response.count
            
            # Unique authors
            authors_response = self.supabase.table('timeline_tweets')\
                .select('author')\
                .execute()
            unique_authors = len(set(tweet['author'] for tweet in authors_response.data if tweet.get('author')))
            
            return {
                'total_tweets': total,
                'unique_authors': unique_authors
            }
        except Exception as e:
            logger.error(f"❌ Error fetching stats: {e}")
            return {
                'total_tweets': 0,
                'unique_authors': 0
            }


def main():
    scraper = TwitterScraperPlaywright()
    result = scraper.scrape_and_save(max_tweets=10)
    
    # Show stats
    stats = scraper.get_stats()
    logger.info(f"\n📊 DATABASE STATS:")
    logger.info(f"   Total tweets in DB: {stats['total_tweets']}")
    logger.info(f"   Unique authors: {stats['unique_authors']}")
    
    return result


if __name__ == "__main__":
    main()



import time
import random
import logging
from datetime import datetime
from app.scraper import TwitterScraperPlaywright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScraperScheduler:
    def __init__(self, base_interval_minutes=10, max_tweets=10):
        """
        Initialize scheduler
        
        Args:
            base_interval_minutes: Base interval between runs (default: 10)
            max_tweets: Number of tweets to collect per run (default: 10)
        """
        self.base_interval = base_interval_minutes * 60  # Convert to seconds
        self.max_tweets = max_tweets
        self.run_count = 0
        
    def get_random_interval(self):
        """
        Calculate random interval to avoid detection
        Range: base_interval ± 20%
        Example: 10 min → 8-12 minutes randomly
        """
        min_interval = self.base_interval * 0.8  # -20%
        max_interval = self.base_interval * 1.2  # +20%
        interval = random.uniform(min_interval, max_interval)
        return interval
    
    def run_once(self):
        """Execute one scraping run"""
        try:
            self.run_count += 1
            logger.info(f"\n{'='*70}")
            logger.info(f"🚀 Starting scrape run #{self.run_count}")
            logger.info(f"{'='*70}")
            
            # Create scraper and run
            scraper = TwitterScraperPlaywright()
            result = scraper.scrape_and_save(max_tweets=self.max_tweets)
            
            # Log results
            logger.info(f"\n{'='*70}")
            logger.info(f"📊 Run #{self.run_count} Summary:")
            logger.info(f"   Collected: {result['total_collected']} tweets")
            logger.info(f"   ✅ Saved: {result['saved']}")
            logger.info(f"   ⏭️  Skipped: {result['skipped_duplicates']}")
            
            # Get overall stats
            stats = scraper.get_stats()
            logger.info(f"   📈 Total in DB: {stats['total_tweets']} tweets")
            logger.info(f"{'='*70}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in run #{self.run_count}: {e}")
            return False
    
    def start(self, max_runs=None):
        """
        Start the scheduler
        
        Args:
            max_runs: Maximum number of runs (None for infinite)
        """
        logger.info("🎯 Twitter Scraper Scheduler Started")
        logger.info(f"⏰ Base interval: {self.base_interval/60:.1f} minutes")
        logger.info(f"📊 Tweets per run: {self.max_tweets}")
        logger.info(f"🎲 Random variation: ±20%")
        if max_runs:
            logger.info(f"🔢 Max runs: {max_runs}")
        else:
            logger.info(f"🔄 Running indefinitely (press Ctrl+C to stop)")
        logger.info(f"{'='*70}\n")
        
        try:
            while True:
                # Check if max runs reached
                if max_runs and self.run_count >= max_runs:
                    logger.info(f"✅ Completed {max_runs} runs. Stopping scheduler.")
                    break
                
                # Run scraper
                success = self.run_once()
                
                # Calculate next run time with random interval
                interval = self.get_random_interval()
                interval_minutes = interval / 60
                next_run = datetime.now().replace(microsecond=0)
                next_run = datetime.fromtimestamp(next_run.timestamp() + interval)
                
                logger.info(f"⏳ Next run in {interval_minutes:.1f} minutes")
                logger.info(f"🕐 Next run at: {next_run.strftime('%I:%M:%S %p')}")
                logger.info(f"{'='*70}\n")
                
                # Wait for next run
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info(f"\n\n{'='*70}")
            logger.info("⏹️  Scheduler stopped by user (Ctrl+C)")
            logger.info(f"📊 Total runs completed: {self.run_count}")
            logger.info(f"{'='*70}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Twitter Scraper Scheduler - Runs automatically with random intervals'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Base interval in minutes between runs (default: 10)'
    )
    parser.add_argument(
        '--tweets',
        type=int,
        default=10,
        help='Number of tweets to collect per run (default: 10)'
    )
    parser.add_argument(
        '--max-runs',
        type=int,
        default=None,
        help='Maximum number of runs (default: infinite)'
    )
    
    args = parser.parse_args()
    
    # Create and start scheduler
    scheduler = ScraperScheduler(
        base_interval_minutes=args.interval,
        max_tweets=args.tweets
    )
    
    scheduler.start(max_runs=args.max_runs)


if __name__ == "__main__":
    main()


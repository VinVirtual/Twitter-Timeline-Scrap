import sys
from app.scraper import TwitterScraperPlaywright

def main():
    max_tweets = 10
    if len(sys.argv) > 1:
        try:
            max_tweets = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default (10)")
    
    print(f"🚀 Starting Twitter Scraper (collecting {max_tweets} tweets)...\n")
    
    scraper = TwitterScraperPlaywright()
    result = scraper.scrape_and_save(max_tweets=max_tweets)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Successfully collected: {result['total_collected']} tweets")
    print(f"💾 Saved to Supabase: {result['saved']} tweets")
    print(f"⏭️  Skipped (duplicates): {result['skipped_duplicates']} tweets")
    
    stats = scraper.get_stats()
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"📊 Total tweets in database: {stats['total_tweets']}")
    print(f"👥 Unique authors: {stats['unique_authors']}")
    
    print("\n✅ Scraping completed!")

if __name__ == "__main__":
    main()


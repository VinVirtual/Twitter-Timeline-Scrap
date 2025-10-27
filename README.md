# Twitter Timeline Scraper

A Python-based tool for scraping tweets from your Twitter timeline and storing them in Supabase with duplicate detection.

## ⚠️ Security Warnings

Before using this tool, please be aware of the following security considerations:

1. **Supabase & API Key Security**:
   - Never commit your `.env` file to version control
   - Keep your Supabase keys secure and rotate them if compromised
   - Monitor your database for any unauthorized access

2. **Chrome Profile Security**:
   - The tool uses your Chrome profile to access Twitter
   - This means it has access to your Twitter session
   - Use a separate Chrome profile for scraping to limit access to your main account
   - Never share your Chrome user data directory

3. **Twitter Terms of Service**:
   - This tool is for educational purposes only
   - Ensure you comply with Twitter's Terms of Service
   - Do not use this tool for:
     - Mass scraping
     - Automated posting
     - Data collection for commercial purposes without permission
     - Any activity that could harm Twitter's services

4. **Best Practices**:
   - Use a dedicated Twitter account for testing
   - Regularly clear your Chrome profile data
   - Monitor your Twitter account for any suspicious activity
   - Keep your ChromeDriver and Chrome browser updated

## ✨ Features

- ✅ Scrape tweets from your Twitter home timeline
- ✅ Extract tweet ID, content, and author
- ✅ Save to Supabase cloud database
- ✅ Automatic duplicate detection and prevention
- ✅ FastAPI REST API for programmatic access
- ✅ Can run repeatedly without duplicates
- ✅ Cloud-based data storage with Supabase dashboard

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account (free tier available)
- Google Chrome browser
- ChromeDriver (matching your Chrome version)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/VinVirtual/Twitter-Timeline-Scrapper-FastAPI.git
cd Twitter-Timeline-Scraper-FastAPI
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Unix or MacOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Supabase

1. **Create Supabase account**: Go to https://supabase.com and sign up
2. **Create new project**: Click "New Project" and wait for setup
3. **Run database schema**:
   - Go to SQL Editor in your Supabase dashboard
   - Copy the contents of `supabase-schema.sql`
   - Paste and run in SQL Editor
4. **Get credentials**:
   - Go to Settings > API
   - Copy `URL` and `anon public` key

### 5. Configure environment variables

```bash
cp env.example .env
```

Edit `.env` with your values:

```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Chrome (update paths for your system)
CHROME_USER_DATA_DIR=/Users/YourUsername/Library/Application Support/Google/Chrome
CHROME_PROFILE_NAME=Default
CHROME_BINARY_LOCATION=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
```

### Finding Chrome Paths

**macOS:**
- User Data: `~/Library/Application Support/Google/Chrome`
- Binary: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- ChromeDriver: Install with `brew install chromedriver`

**Windows:**
- User Data: `C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data`
- Binary: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- ChromeDriver: Download from https://chromedriver.chromium.org/

**Linux:**
- User Data: `~/.config/google-chrome`
- Binary: `/usr/bin/google-chrome`
- ChromeDriver: `sudo apt install chromium-chromedriver`

## 📖 Usage

### Option 1: Simple Run Script (Easiest)

```bash
# Scrape 10 tweets (default)
python run_scraper.py

# Scrape custom number of tweets
python run_scraper.py 20
```

### Option 2: Python Script

```python
from app.scraper import TwitterScraperSupabase

# Create scraper
scraper = TwitterScraperSupabase()

# Scrape 10 tweets from your timeline
result = scraper.scrape_and_save(max_tweets=10)

print(f"Saved: {result['saved']}")
print(f"Skipped (duplicates): {result['skipped_duplicates']}")

# Get all tweets from database
tweets = scraper.get_all_tweets()

# Get statistics
stats = scraper.get_stats()
print(f"Total tweets: {stats['total_tweets']}")
```

### Option 3: FastAPI Server

Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

API Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| POST | `/scrape?max_tweets=10` | Scrape tweets from timeline |
| GET | `/tweets?limit=100` | Get all tweets |
| GET | `/tweets/recent?limit=10` | Get recent tweets |
| GET | `/tweets/author/{username}` | Get tweets by author |
| GET | `/stats` | Database statistics |
| DELETE | `/tweets/{tweet_id}` | Delete specific tweet |
| GET | `/health` | Health check |

**Example API calls:**
```bash
# Scrape 10 tweets
curl -X POST "http://localhost:8000/scrape?max_tweets=10"

# Get all tweets
curl "http://localhost:8000/tweets"

# Get stats
curl "http://localhost:8000/stats"

# Get tweets by author
curl "http://localhost:8000/tweets/author/elonmusk"
```

## 📊 Database Schema

The scraper creates a `timeline_tweets` table in Supabase:

```sql
CREATE TABLE timeline_tweets (
  id BIGSERIAL PRIMARY KEY,
  tweet_id VARCHAR(50) UNIQUE NOT NULL,
  content TEXT NOT NULL,
  author VARCHAR(50),
  tweet_url TEXT,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔄 How It Works

1. **Opens Twitter**: Uses Selenium with your Chrome profile
2. **Scrolls timeline**: Collects specified number of tweets
3. **Extracts data**: Gets tweet ID from `/status/` URL, content, and author
4. **Checks duplicates**: Queries Supabase for existing tweet_id
5. **Saves to database**: Inserts new tweets, skips duplicates
6. **Returns results**: Summary of saved vs skipped tweets

## 📈 Example Output

```
🚀 Starting tweet collection (max: 10)...
📊 Found 20 tweet elements on page
📥 Collected tweet 1/10: 1234567890 by @elonmusk
📥 Collected tweet 2/10: 1234567891 by @naval
✅ Collected 10 tweets

✅ Saved new tweet: 1234567890 by @elonmusk
⏭️  Skipping duplicate tweet: 1234567892
✅ Saved new tweet: 1234567893 by @sama

==================================================
📊 SCRAPING SUMMARY:
   Total Collected: 10
   ✅ Saved: 8
   ⏭️  Skipped (duplicates): 2
==================================================

📊 DATABASE STATS:
   Total tweets in database: 45
   Unique authors: 12
```

## 🎨 View Data in Supabase

1. Go to your Supabase project dashboard
2. Click "Table Editor" in the sidebar
3. Select "timeline_tweets" table
4. View, filter, and export your scraped tweets

## 🔍 Query Examples

In Supabase SQL Editor:

```sql
-- Get all tweets
SELECT * FROM timeline_tweets ORDER BY scraped_at DESC;

-- Count tweets by author
SELECT author, COUNT(*) as count 
FROM timeline_tweets 
GROUP BY author 
ORDER BY count DESC;

-- Get today's tweets
SELECT * FROM timeline_tweets 
WHERE scraped_at >= CURRENT_DATE;

-- Use built-in views
SELECT * FROM recent_timeline_tweets;
SELECT * FROM tweets_by_author;
```

## ⏰ Schedule Regular Scraping

### Using cron (Mac/Linux):
```bash
# Edit crontab
crontab -e

# Run every 10 minutes
*/10 * * * * cd /path/to/project && python -c "from app.scraper import TwitterScraperSupabase; TwitterScraperSupabase().scrape_and_save(max_tweets=10)"
```

### Using Task Scheduler (Windows):
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., every 10 minutes)
4. Action: Start a program
5. Program: `python`
6. Arguments: `-c "from app.scraper import TwitterScraperSupabase; TwitterScraperSupabase().scrape_and_save(max_tweets=10)"`

## 🛠️ Project Structure

```
Twitter-Timeline-Scraper-FastAPI/
├── app/
│   ├── __init__.py
│   ├── scraper.py              # Main scraper with Supabase
│   └── main.py                 # FastAPI server
├── run_scraper.py              # Simple run script
├── supabase-schema.sql         # Database schema
├── env.example                 # Environment template
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔧 Troubleshooting

### Can't connect to Supabase
- Check your `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- Verify you ran the SQL schema in Supabase
- Check your internet connection

### Chrome/ChromeDriver issues
- Make sure Chrome is installed
- Verify ChromeDriver version matches Chrome version
- Check Chrome paths in `.env` are correct
- Ensure you're logged into Twitter in that Chrome profile

### No tweets collected
- Make sure you're logged into Twitter in the specified Chrome profile
- Check that `CHROME_PROFILE_NAME` is correct
- Try opening Chrome manually with that profile first

### Duplicate errors
- This is expected behavior! The scraper skips duplicates
- Check the logs to see which tweets were skipped

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Please ensure you comply with Twitter's Terms of Service and API usage guidelines when using this scraper. The authors are not responsible for any misuse of this tool or any consequences resulting from such misuse.

## 🎯 Built With

- **Selenium** - Web scraping automation
- **FastAPI** - Modern web framework
- **Supabase** - Cloud PostgreSQL database
- **Python** - Programming language

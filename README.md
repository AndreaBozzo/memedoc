# MemeDoc - Automated Meme Data Collection

🤖 Automated system for collecting and analyzing meme trends across platforms using computer vision and natural language processing.

## Features

- **Automated Reddit Collection**: Scrapes r/memes every 2 hours via GitHub Actions
- **Image Analysis**: Computer vision with OpenCV for template detection and similarity matching
- **Duplicate Detection**: Prevents re-inserting same memes across collection runs
- **Cloud Database**: Persistent PostgreSQL storage via Supabase (100% free)
- **Data Export**: Automatic JSON exports for analysis
- **Template Matching**: Perceptual hashing to identify meme template variations

## Architecture

- **Data Collection**: Python + PRAW (Reddit API)
- **Image Processing**: OpenCV + ImageHash for computer vision
- **Database**: Supabase PostgreSQL (cloud-hosted)
- **Automation**: GitHub Actions (runs every 2 hours)
- **Export**: JSON format for data analysis

## Setup

1. **Create Supabase account** and project
2. **Run SQL schema** from `supabase_setup.py`
3. **Configure GitHub Secrets**:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
4. **Push to GitHub** - Actions will start automatically

## Local Development

```bash
# Setup
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Configure .env
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

# Run collection
python main.py
```

## Data Structure

Each meme post includes:
- Platform metadata (Reddit post ID, score, timestamp)
- Image analysis (perceptual hashes, template structure)
- Computer vision features for similarity detection

## Automation

- **Frequency**: Every 2 hours via GitHub Actions
- **Cost**: 100% free (GitHub Actions + Supabase free tiers)
- **Monitoring**: Automatic failure notifications
- **Data Export**: JSON artifacts downloadable from Actions runs

---

🤖 *Generated with [Claude Code](https://claude.ai/code)*
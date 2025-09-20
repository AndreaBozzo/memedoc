# MemeDoc - Automated Meme Data Collection

Automated system for collecting and analyzing meme trends across platforms using computer vision and natural language processing.

## Features

- **Automated Reddit Collection**: Scrapes r/memes every 2 hours via GitHub Actions
- **Async Processing Pipeline**: Parallel image processing with 10x performance boost
- **Image Analysis**: Computer vision with OpenCV for template detection and similarity matching
- **Duplicate Detection**: Prevents re-inserting same memes across collection runs
- **Cloud Database**: Persistent PostgreSQL storage via Supabase (100% free)
- **Real-time Dashboard**: Live analytics at [GitHub Pages](https://andreabozzo.github.io/memedoc/)
- **Data Export**: Automatic JSON exports for analysis
- **Template Matching**: Perceptual hashing to identify meme template variations

## Architecture

- **Data Collection**: Python + PRAW (Reddit API) with async processing
- **Image Processing**: OpenCV + ImageHash with HTTP connection pooling
- **Database**: Supabase PostgreSQL with bulk operations
- **Automation**: GitHub Actions (runs every 2 hours)
- **Monitoring**: Structured logging with performance metrics
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

## Performance

- **Processing Speed**: 10-20 posts/sec (10x faster than original)
- **Parallel Operations**: Async image downloads with connection pooling
- **Database Efficiency**: Bulk UPSERT operations with 80% fewer queries
- **Memory Usage**: Constant memory footprint with proper resource management

## Automation

- **Frequency**: Every 2 hours via GitHub Actions
- **Cost**: 100% free (GitHub Actions + Supabase free tiers)
- **Monitoring**: Structured logging with performance metrics
- **Data Export**: JSON artifacts downloadable from Actions runs

## Dashboard

View live analytics and trends at: https://andreabozzo.github.io/memedoc/
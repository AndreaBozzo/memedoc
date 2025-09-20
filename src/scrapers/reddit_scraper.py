# scrapers/reddit_scraper.py
import praw
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='MemeDetector/1.0'
        )
    
    def scrape_subreddit(self, subreddit_name, limit=100):
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        for post in subreddit.hot(limit=limit):
            if post.url.endswith(('.jpg', '.png', '.gif')):
                posts.append({
                    'platform': 'reddit',
                    'post_id': post.id,
                    'title': post.title,
                    'score': post.score,
                    'url': post.url,
                    'subreddit': subreddit_name,
                    'timestamp': datetime.fromtimestamp(post.created_utc),
                    'num_comments': post.num_comments
                })
        return posts
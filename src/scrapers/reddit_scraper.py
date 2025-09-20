import praw
from datetime import datetime
import os
from typing import List, Optional, Any, Dict
from dotenv import load_dotenv
from .base_scraper import BaseScraper, ScrapedPost

load_dotenv()

class RedditScraper(BaseScraper):
    """Reddit platform scraper implementing BaseScraper interface"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.reddit = None

    def authenticate(self) -> bool:
        """Authenticate with Reddit API"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=self.config.get('user_agent', 'MemeDetector/1.0')
            )
            # Test connection
            self.reddit.user.me()
            return True
        except Exception as e:
            self.logger.error(f"Reddit authentication failed: {e}")
            return False

    def scrape_posts(
        self,
        source: str,
        limit: int = 100,
        sort_type: str = 'hot',
        **kwargs
    ) -> List[ScrapedPost]:
        """Scrape posts from a subreddit"""
        if not self.reddit:
            if not self.authenticate():
                return []

        try:
            subreddit = self.reddit.subreddit(source)
            posts = []

            # Get posts based on sort type
            if sort_type == 'hot':
                post_iterator = subreddit.hot(limit=limit)
            elif sort_type == 'new':
                post_iterator = subreddit.new(limit=limit)
            elif sort_type == 'top':
                time_filter = kwargs.get('time_filter', 'day')
                post_iterator = subreddit.top(time_filter=time_filter, limit=limit)
            else:
                post_iterator = subreddit.hot(limit=limit)

            posts_found = 0
            posts_processed = 0

            for post in post_iterator:
                posts_found += 1

                if self.is_media_post(post):
                    scraped_post = ScrapedPost(
                        platform='reddit',
                        post_id=post.id,
                        title=post.title,
                        url=post.url,
                        score=post.score,
                        timestamp=datetime.fromtimestamp(post.created_utc),
                        author=str(post.author) if post.author else None,
                        content=post.selftext if hasattr(post, 'selftext') else None,
                        tags=[source],  # subreddit as tag
                        metadata={
                            'subreddit': source,
                            'num_comments': post.num_comments,
                            'upvote_ratio': getattr(post, 'upvote_ratio', None),
                            'post_hint': getattr(post, 'post_hint', None),
                            'sort_type': sort_type
                        }
                    )
                    posts.append(scraped_post)
                    posts_processed += 1

            self.log_scraping_stats(source, posts_found, posts_processed)
            return posts

        except Exception as e:
            self.logger.error(f"Failed to scrape r/{source}: {e}")
            return []

    def get_post_details(self, post_id: str) -> Optional[ScrapedPost]:
        """Get detailed information for a specific Reddit post"""
        if not self.reddit:
            if not self.authenticate():
                return None

        try:
            submission = self.reddit.submission(id=post_id)

            if self.is_media_post(submission):
                return ScrapedPost(
                    platform='reddit',
                    post_id=submission.id,
                    title=submission.title,
                    url=submission.url,
                    score=submission.score,
                    timestamp=datetime.fromtimestamp(submission.created_utc),
                    author=str(submission.author) if submission.author else None,
                    content=submission.selftext,
                    tags=[submission.subreddit.display_name],
                    metadata={
                        'subreddit': submission.subreddit.display_name,
                        'num_comments': submission.num_comments,
                        'upvote_ratio': submission.upvote_ratio,
                        'post_hint': getattr(submission, 'post_hint', None)
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to get Reddit post {post_id}: {e}")
            return None

    def is_media_post(self, post_data: Any) -> bool:
        """Check if Reddit post contains image/video content"""
        if hasattr(post_data, 'url'):
            url = post_data.url.lower()
            # Direct image/video links
            if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm')):
                return True
            # Reddit image/video domains
            if any(domain in url for domain in ['i.redd.it', 'v.redd.it', 'imgur.com']):
                return True
            # Check post hint
            if hasattr(post_data, 'post_hint'):
                return post_data.post_hint in ['image', 'hosted:video', 'rich:video']

        return False

    def get_supported_sources(self) -> List[str]:
        """Return list of supported subreddits"""
        return self.config.get('supported_subreddits', ['memes', 'dankmemes', 'wholesomememes'])
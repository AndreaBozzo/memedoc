from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ScrapedPost:
    """Standardized post data structure across all platforms"""

    def __init__(
        self,
        platform: str,
        post_id: str,
        title: str,
        url: str,
        score: int,
        timestamp: datetime,
        author: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.platform = platform
        self.post_id = post_id
        self.title = title
        self.url = url
        self.score = score
        self.timestamp = timestamp
        self.author = author
        self.content = content
        self.tags = tags or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'platform': self.platform,
            'post_id': self.post_id,
            'title': self.title,
            'url': self.url,
            'score': self.score,
            'timestamp': self.timestamp,
            'author': self.author,
            'content': self.content,
            'tags': self.tags,
            'metadata': self.metadata
        }

class BaseScraper(ABC):
    """Abstract base class for all platform scrapers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform_name = config.get('platform_name', 'unknown')
        self.rate_limit = config.get('rate_limit', 60)  # requests per minute
        self.logger = logging.getLogger(f"{__name__}.{self.platform_name}")

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API"""
        pass

    @abstractmethod
    def scrape_posts(
        self,
        source: str,
        limit: int = 100,
        **kwargs
    ) -> List[ScrapedPost]:
        """Scrape posts from specified source (subreddit, hashtag, etc.)"""
        pass

    @abstractmethod
    def get_post_details(self, post_id: str) -> Optional[ScrapedPost]:
        """Get detailed information for a specific post"""
        pass

    @abstractmethod
    def is_media_post(self, post_data: Any) -> bool:
        """Check if post contains image/video content"""
        pass

    def health_check(self) -> bool:
        """Verify scraper can connect to platform"""
        try:
            return self.authenticate()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def get_supported_sources(self) -> List[str]:
        """Return list of sources this scraper can handle"""
        return self.config.get('supported_sources', [])

    def get_rate_limit_info(self) -> Dict[str, int]:
        """Return rate limiting information"""
        return {
            'requests_per_minute': self.rate_limit,
            'daily_limit': self.config.get('daily_limit', 10000)
        }

    def log_scraping_stats(self, source: str, posts_found: int, posts_processed: int):
        """Log scraping statistics"""
        self.logger.info(
            f"Scraped {source}: {posts_found} found, {posts_processed} processed"
        )
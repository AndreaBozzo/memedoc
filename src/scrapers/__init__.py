# Auto-register all scrapers
import json
import os
from .scraper_registry import ScraperRegistry, register_scraper
from .reddit_scraper import RedditScraper

# Register Reddit scraper
@register_scraper('reddit')
class RegisteredRedditScraper(RedditScraper):
    pass

def load_platform_config(platform_name: str) -> dict:
    """Load configuration for a platform"""
    config_path = os.path.join('config', 'platforms', f'{platform_name}.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback default config
        return {
            'platform_name': platform_name,
            'enabled': True,
            'rate_limit': 60,
            'daily_limit': 1000
        }

def get_scraper(platform_name: str):
    """Factory function to get configured scraper"""
    config = load_platform_config(platform_name)
    return ScraperRegistry.get_scraper(platform_name, config)
from typing import Dict, Type, List, Optional
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class ScraperRegistry:
    """Registry pattern for managing platform scrapers"""

    _instance = None
    _scrapers: Dict[str, Type[BaseScraper]] = {}
    _instances: Dict[str, BaseScraper] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, platform_name: str, scraper_class: Type[BaseScraper]):
        """Register a scraper class for a platform"""
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError(f"Scraper must inherit from BaseScraper")

        cls._scrapers[platform_name] = scraper_class
        logger.info(f"Registered scraper for platform: {platform_name}")

    @classmethod
    def get_scraper(cls, platform_name: str, config: Dict) -> Optional[BaseScraper]:
        """Get a scraper instance for the specified platform"""
        if platform_name not in cls._scrapers:
            logger.error(f"No scraper registered for platform: {platform_name}")
            return None

        # Return existing instance or create new one
        if platform_name not in cls._instances:
            scraper_class = cls._scrapers[platform_name]
            try:
                cls._instances[platform_name] = scraper_class(config)
                logger.info(f"Created scraper instance for: {platform_name}")
            except Exception as e:
                logger.error(f"Failed to create scraper for {platform_name}: {e}")
                return None

        return cls._instances[platform_name]

    @classmethod
    def get_available_platforms(cls) -> List[str]:
        """Get list of registered platform names"""
        return list(cls._scrapers.keys())

    @classmethod
    def health_check_all(cls) -> Dict[str, bool]:
        """Run health checks on all registered scrapers"""
        results = {}
        for platform_name in cls._scrapers:
            instance = cls._instances.get(platform_name)
            if instance:
                results[platform_name] = instance.health_check()
            else:
                results[platform_name] = False
        return results

    @classmethod
    def reset(cls):
        """Reset registry (mainly for testing)"""
        cls._scrapers.clear()
        cls._instances.clear()


def register_scraper(platform_name: str):
    """Decorator for automatic scraper registration"""
    def decorator(scraper_class: Type[BaseScraper]):
        ScraperRegistry.register(platform_name, scraper_class)
        return scraper_class
    return decorator
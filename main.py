import asyncio
from src.scrapers import get_scraper
from src.processors.image_analyzer import ImageTemplateDetector
from src.core.async_processor import AsyncProcessor
from src.core.logging_config import MemeDocLogger
from src.core.config_manager import config_manager
from supabase_setup import SupabaseClient

async def process_new_memes():
    """Async version with parallel processing"""
    logger = MemeDocLogger('main_optimized')

    # Initialize components
    db = SupabaseClient()
    image_analyzer = ImageTemplateDetector()

    # Get enabled platforms
    enabled_platforms = config_manager.get_all_enabled_platforms()
    if not enabled_platforms:
        enabled_platforms = ['reddit']  # fallback

    logger.logger.info(f"Processing platforms: {enabled_platforms}")

    total_stats = {
        'total_processed': 0,
        'total_new': 0,
        'total_time': 0
    }

    # Process each platform
    for platform_name in enabled_platforms:
        platform_config = config_manager.get_platform_config(platform_name)

        if not platform_config.enabled:
            continue

        logger.log_scraping_start(platform_name, platform_config.daily_limit)

        try:
            # Get scraper
            scraper = get_scraper(platform_name)
            if not scraper:
                logger.log_error(Exception(f"Failed to initialize {platform_name} scraper"))
                continue

            # Scrape posts
            scraped_posts = scraper.scrape_posts('memes', limit=min(100, platform_config.daily_limit))

            if not scraped_posts:
                logger.logger.info(f"No posts scraped from {platform_name}")
                continue

            # Process posts with async pipeline
            async with AsyncProcessor(max_workers=10, max_concurrent_downloads=5) as processor:
                stats = await processor.process_posts_batch(scraped_posts, image_analyzer, db)

                # Log results
                logger.log_scraping_result(
                    platform_name,
                    stats['total_processed'],
                    stats['new_posts'],
                    stats['processing_time']
                )

                # Performance warnings
                if stats['posts_per_second'] < 1.0:
                    logger.log_performance_warning(
                        'posts_per_second',
                        stats['posts_per_second'],
                        1.0
                    )

                # Update totals
                total_stats['total_processed'] += stats['total_processed']
                total_stats['total_new'] += stats['new_posts']
                total_stats['total_time'] += stats['processing_time']

        except Exception as e:
            logger.log_error(e, f"Platform: {platform_name}")

    # Final summary
    overall_rate = total_stats['total_processed'] / total_stats['total_time'] if total_stats['total_time'] > 0 else 0
    logger.logger.info(
        f"Session completed | "
        f"Total processed: {total_stats['total_processed']} | "
        f"Total new: {total_stats['total_new']} | "
        f"Overall rate: {overall_rate:.1f} posts/s"
    )

    # Get and display stats
    try:
        db_stats = db.get_stats()
        logger.logger.info(f"Database total: {db_stats['total_posts']} posts")

        if db_stats['top_posts']:
            logger.logger.info("Top memes:")
            for meme in db_stats['top_posts'][:3]:
                logger.logger.info(f"  - {meme['title'][:50]}... (Score: {meme['score']})")

        # Export data
        exported = db.export_data()
        logger.logger.info(f"Exported {exported} records to meme_export.json")

    except Exception as e:
        logger.log_error(e, "Getting final stats")

if __name__ == "__main__":
    asyncio.run(process_new_memes())
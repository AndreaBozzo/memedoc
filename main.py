from src.scrapers import get_scraper
from src.processors.image_analyzer import ImageTemplateDetector
from supabase_setup import SupabaseClient

def process_new_memes():
    # Initialize components with new architecture
    db = SupabaseClient()
    scraper = get_scraper('reddit')
    image_analyzer = ImageTemplateDetector()

    if not scraper:
        print("❌ Failed to initialize Reddit scraper")
        return

    # Scrape new posts using new interface
    scraped_posts = scraper.scrape_posts('memes', limit=100)

    new_posts_count = 0
    for scraped_post in scraped_posts:
        # Convert ScrapedPost to dict for compatibility
        post_dict = scraped_post.to_dict()

        # Extract image features
        features = image_analyzer.extract_features(post_dict['url'])
        if features:
            # Flatten features into post data
            post_dict['template_hash'] = features['phash']
            post_dict['phash'] = features['phash']
            post_dict['dhash'] = features['dhash']
            post_dict['whash'] = features['whash']
            post_dict['colorhash'] = features['colorhash']
            post_dict['template_structure'] = features['template_structure']

            # Save to Supabase (returns None if duplicate)
            result = db.create_meme_post(**post_dict)
            if result is not None:
                new_posts_count += 1

    print(f"Processed {len(scraped_posts)} posts, {new_posts_count} new posts added")

    # Get stats
    stats = db.get_stats()
    print(f"Total in database: {stats['total_posts']}")

    if stats['top_posts']:
        print("Top memes:")
        for meme in stats['top_posts'][:3]:
            print(f"  - {meme['title'][:50]}... (Score: {meme['score']})")

    # Export data
    exported = db.export_data()
    print(f"Exported {exported} records to meme_export.json")

if __name__ == "__main__":
    process_new_memes()
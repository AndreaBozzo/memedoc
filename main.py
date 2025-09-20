from src.scrapers.reddit_scraper import RedditScraper
from src.processors.image_analyzer import ImageTemplateDetector
from supabase_setup import SupabaseClient

def process_new_memes():
    # Initialize components (Supabase instead of Neo4j)
    db = SupabaseClient()
    scraper = RedditScraper()
    image_analyzer = ImageTemplateDetector()

    # Scrape new posts
    posts = scraper.scrape_subreddit('memes', limit=100)

    new_posts_count = 0
    for post in posts:
        # Extract image features
        features = image_analyzer.extract_features(post['url'])
        if features:
            # Flatten features into post data
            post['template_hash'] = features['phash']
            post['phash'] = features['phash']
            post['dhash'] = features['dhash']
            post['whash'] = features['whash']
            post['colorhash'] = features['colorhash']
            post['template_structure'] = features['template_structure']

            # Save to Supabase (returns None if duplicate)
            result = db.create_meme_post(**post)
            if result is not None:
                new_posts_count += 1

    print(f"Processed {len(posts)} posts, {new_posts_count} new posts added")

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
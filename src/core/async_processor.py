import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time
from ..scrapers.base_scraper import ScrapedPost

class AsyncProcessor:
    """Async pipeline for parallel processing of scraped posts"""

    def __init__(self, max_workers: int = 10, max_concurrent_downloads: int = 5):
        self.max_workers = max_workers
        self.max_concurrent_downloads = max_concurrent_downloads
        self.session: Optional[aiohttp.ClientSession] = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_downloads)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'MemeDoc/1.0'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)

    async def process_posts_batch(self, posts: List[ScrapedPost], image_analyzer, db_client) -> Dict[str, int]:
        """Process posts in parallel batches"""
        start_time = time.time()

        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

        # Process all posts concurrently
        tasks = [
            self._process_single_post(post, image_analyzer, semaphore)
            for post in posts
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Batch database operations
        successful_posts = []
        for post, result in zip(posts, results):
            if isinstance(result, dict) and result.get('success'):
                successful_posts.append({
                    'post': post,
                    'features': result.get('features', {})
                })

        # Bulk insert to database
        new_count = await self._bulk_insert_posts(successful_posts, db_client)

        processing_time = time.time() - start_time

        return {
            'total_processed': len(posts),
            'successful': len(successful_posts),
            'new_posts': new_count,
            'processing_time': processing_time,
            'posts_per_second': len(posts) / processing_time if processing_time > 0 else 0
        }

    async def _process_single_post(self, post: ScrapedPost, image_analyzer, semaphore) -> Dict[str, Any]:
        """Process a single post with feature extraction"""
        async with semaphore:
            try:
                # Download image asynchronously
                image_data = await self._download_image(post.url)
                if not image_data:
                    return {'success': False, 'error': 'Failed to download image'}

                # Extract features in thread pool (CPU-bound)
                loop = asyncio.get_event_loop()
                features = await loop.run_in_executor(
                    self.executor,
                    image_analyzer.extract_features_from_bytes,
                    image_data
                )

                return {
                    'success': True,
                    'features': features or {}
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image with connection pooling"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                return None
        except Exception:
            return None

    async def _bulk_insert_posts(self, posts_with_features: List[Dict], db_client) -> int:
        """Bulk insert posts to database"""
        if not posts_with_features:
            return 0

        # Prepare batch data
        batch_data = []
        for item in posts_with_features:
            post = item['post']
            features = item['features']

            post_data = {
                'platform': post.platform,
                'post_id': post.post_id,
                'title': post.title,
                'url': post.url,
                'score': post.score,
                'timestamp': post.timestamp.isoformat() if post.timestamp else None,
                'template_hash': features.get('phash'),
                'phash': features.get('phash'),
                'dhash': features.get('dhash'),
                'whash': features.get('whash'),
                'colorhash': features.get('colorhash'),
                'template_structure': features.get('template_structure')
            }
            batch_data.append(post_data)

        # Execute bulk upsert in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            db_client.bulk_upsert_posts,
            batch_data
        )
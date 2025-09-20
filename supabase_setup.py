import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Free PostgreSQL alternative to Neo4j"""

    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')

        if not url or not key:
            raise ValueError(f"Missing Supabase credentials. URL: {url}, Key: {'***' if key else None}")

        self.supabase: Client = create_client(url, key)

    def create_meme_post(self, **kwargs):
        """Insert meme post (skip duplicates)"""
        try:
            # Check if exists
            existing = self.supabase.table('meme_posts').select('id').eq(
                'platform', kwargs.get('platform')
            ).eq('post_id', kwargs.get('post_id')).execute()

            if existing.data:
                return None  # Skip duplicate

            # Insert new
            result = self.supabase.table('meme_posts').insert({
                'platform': kwargs.get('platform'),
                'post_id': kwargs.get('post_id'),
                'title': kwargs.get('title'),
                'score': kwargs.get('score'),
                'url': kwargs.get('url'),
                'timestamp': kwargs.get('timestamp').isoformat() if kwargs.get('timestamp') else None,
                'template_hash': kwargs.get('template_hash'),
                'phash': kwargs.get('phash'),
                'dhash': kwargs.get('dhash'),
                'template_structure': kwargs.get('template_structure')
            }).execute()

            return result.data[0] if result.data else None

        except Exception as e:
            print(f"Error inserting meme: {e}")
            return None

    def get_recent_posts(self, hours=24):
        """Get recent posts"""
        try:
            result = self.supabase.table('meme_posts').select('*').gte(
                'timestamp',
                (datetime.now() - timedelta(hours=hours)).isoformat()
            ).order('timestamp', desc=True).execute()

            return result.data
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []

    def get_stats(self):
        """Get database statistics"""
        try:
            # Total count
            total = self.supabase.table('meme_posts').select('id', count='exact').execute()

            # Top scores
            top_posts = self.supabase.table('meme_posts').select('title,score').order(
                'score', desc=True
            ).limit(5).execute()

            # Template distribution
            templates = self.supabase.rpc('get_template_stats', {}).execute()

            return {
                'total_posts': total.count,
                'top_posts': top_posts.data,
                'templates': templates.data if templates.data else []
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'total_posts': 0, 'top_posts': [], 'templates': []}

    def bulk_upsert_posts(self, posts_data: list) -> int:
        """Bulk upsert posts using PostgreSQL UPSERT (ON CONFLICT)"""
        if not posts_data:
            return 0

        try:
            # Use upsert with conflict resolution
            result = self.supabase.table('meme_posts').upsert(
                posts_data,
                on_conflict='platform,post_id'
            ).execute()

            return len(result.data) if result.data else 0

        except Exception as e:
            print(f"Error bulk upserting posts: {e}")
            # Fallback to individual inserts if bulk fails
            success_count = 0
            for post_data in posts_data:
                try:
                    existing = self.supabase.table('meme_posts').select('id').eq(
                        'platform', post_data['platform']
                    ).eq('post_id', post_data['post_id']).execute()

                    if not existing.data:
                        result = self.supabase.table('meme_posts').insert(post_data).execute()
                        if result.data:
                            success_count += 1
                except Exception:
                    continue

            return success_count

    def export_data(self):
        """Export all data to JSON"""
        try:
            result = self.supabase.table('meme_posts').select('*').execute()

            with open('meme_export.json', 'w') as f:
                json.dump(result.data, f, indent=2, default=str)

            return len(result.data)
        except Exception as e:
            print(f"Error exporting: {e}")
            return 0

# SQL schema for Supabase
SUPABASE_SCHEMA = """
-- Create meme_posts table
CREATE TABLE meme_posts (
    id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL,
    post_id TEXT NOT NULL,
    title TEXT,
    score INTEGER,
    url TEXT,
    timestamp TIMESTAMP,
    template_hash TEXT,
    phash TEXT,
    dhash TEXT,
    whash TEXT,
    colorhash TEXT,
    template_structure TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, post_id)
);

-- Create index for faster queries
CREATE INDEX idx_meme_posts_timestamp ON meme_posts(timestamp DESC);
CREATE INDEX idx_meme_posts_score ON meme_posts(score DESC);
CREATE INDEX idx_meme_posts_template ON meme_posts(template_hash);

-- Function for template stats
CREATE OR REPLACE FUNCTION get_template_stats()
RETURNS TABLE(template_structure TEXT, count BIGINT, avg_score NUMERIC)
LANGUAGE SQL
AS $$
    SELECT
        template_structure,
        COUNT(*) as count,
        AVG(score) as avg_score
    FROM meme_posts
    WHERE template_structure IS NOT NULL
    GROUP BY template_structure
    ORDER BY count DESC;
$$;

-- Enable Row Level Security (optional)
ALTER TABLE meme_posts ENABLE ROW LEVEL SECURITY;
"""
-- Fixed Analytics queries for MemeDoc Supabase schema
-- Run these in Supabase SQL Editor

-- 1. Top performing memes by score
CREATE OR REPLACE VIEW top_memes AS
SELECT
    title,
    score,
    url,
    timestamp,
    template_structure,
    platform,
    post_id
FROM meme_posts
ORDER BY score DESC;

-- 2. Meme velocity (posts per hour)
CREATE OR REPLACE VIEW meme_velocity AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as posts_count,
    AVG(score) as avg_score,
    MAX(score) as max_score
FROM meme_posts
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- 3. Template popularity analysis
CREATE OR REPLACE VIEW template_analysis AS
SELECT
    template_structure,
    COUNT(*) as usage_count,
    AVG(score) as avg_score,
    MAX(score) as best_score,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen
FROM meme_posts
WHERE template_structure IS NOT NULL
GROUP BY template_structure
ORDER BY usage_count DESC;

-- 4. Daily meme stats
CREATE OR REPLACE VIEW daily_stats AS
SELECT
    DATE(timestamp) as day,
    COUNT(*) as total_memes,
    AVG(score) as avg_score,
    MAX(score) as top_score,
    COUNT(DISTINCT template_hash) as unique_templates
FROM meme_posts
GROUP BY DATE(timestamp)
ORDER BY day DESC;

-- 5. Score distribution analysis
CREATE OR REPLACE VIEW score_distribution AS
SELECT
    CASE
        WHEN score < 100 THEN '0-99'
        WHEN score < 500 THEN '100-499'
        WHEN score < 1000 THEN '500-999'
        WHEN score < 5000 THEN '1K-5K'
        WHEN score < 10000 THEN '5K-10K'
        ELSE '10K+'
    END as score_range,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM meme_posts), 2) as percentage
FROM meme_posts
GROUP BY score_range
ORDER BY MIN(score);

-- 6. Dashboard stats
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM meme_posts) as total_memes,
    (SELECT ROUND(AVG(score), 2) FROM meme_posts) as avg_score,
    (SELECT MAX(score) FROM meme_posts) as top_score,
    (SELECT COUNT(DISTINCT template_structure) FROM meme_posts WHERE template_structure IS NOT NULL) as unique_templates,
    (SELECT COUNT(*) FROM meme_posts WHERE timestamp > NOW() - INTERVAL '24 hours') as last_24h,
    (SELECT COUNT(*) FROM meme_posts WHERE timestamp > NOW() - INTERVAL '1 hour') as last_hour;

-- 7. Template evolution tracking
CREATE OR REPLACE VIEW template_evolution AS
SELECT
    template_hash,
    COUNT(*) as variations,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen,
    AVG(score) as avg_performance,
    MIN(score) as min_score,
    MAX(score) as max_score
FROM meme_posts
WHERE template_hash IS NOT NULL
GROUP BY template_hash
HAVING COUNT(*) > 1
ORDER BY variations DESC;

-- 8. Recent activity
CREATE OR REPLACE VIEW recent_activity AS
SELECT
    title,
    score,
    template_structure,
    timestamp,
    EXTRACT(EPOCH FROM (NOW() - timestamp))/3600 as hours_ago
FROM meme_posts
WHERE timestamp > NOW() - INTERVAL '48 hours'
ORDER BY timestamp DESC;

-- 9. High performers (top 10%)
CREATE OR REPLACE VIEW high_performers AS
SELECT
    title,
    score,
    template_structure,
    timestamp,
    post_id
FROM meme_posts
WHERE score > (
    SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY score)
    FROM meme_posts
)
ORDER BY score DESC;

-- 10. Trending function (high score per time ratio)
CREATE OR REPLACE FUNCTION get_trending_memes(hours_window INTEGER DEFAULT 24)
RETURNS TABLE(
    post_id TEXT,
    title TEXT,
    score INTEGER,
    velocity NUMERIC,
    template_structure TEXT,
    hours_old NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mp.post_id,
        mp.title,
        mp.score,
        (mp.score::NUMERIC / GREATEST(EXTRACT(EPOCH FROM (NOW() - mp.timestamp)) / 3600, 1)) as velocity,
        mp.template_structure,
        EXTRACT(EPOCH FROM (NOW() - mp.timestamp))/3600 as hours_old
    FROM meme_posts mp
    WHERE mp.timestamp > NOW() - INTERVAL '1 hour' * hours_window
    AND mp.score > 50
    ORDER BY velocity DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;
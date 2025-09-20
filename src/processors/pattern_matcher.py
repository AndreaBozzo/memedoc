# processors/pattern_matcher.py
from collections import defaultdict
from datetime import datetime, timedelta
import math

class MemePatternMatcher:
    def __init__(self, neo4j_client):
        self.db = neo4j_client
    
    def detect_emerging_patterns(self, time_window_hours=48):
        """Trova meme che mostrano momentum cross-platform"""
        
        # Query Neo4j per meme recenti
        query = """
        MATCH (p:MemePost)
        WHERE p.timestamp > datetime() - duration({hours: $hours})
        RETURN p.platform, p.template_hash, p.title, p.score, p.timestamp
        ORDER BY p.timestamp DESC
        """
        
        results = self.db.run_query(query, hours=time_window_hours)
        
        # Group by template
        template_activity = defaultdict(lambda: {
            'platforms': set(),
            'posts': [],
            'momentum_score': 0,
            'first_seen': None,
            'platform_sequence': []
        })
        
        for record in results:
            template_hash = record['template_hash']
            platform = record['platform']
            timestamp = record['timestamp']
            
            template_data = template_activity[template_hash]
            template_data['platforms'].add(platform)
            template_data['posts'].append(record)
            
            if not template_data['first_seen'] or timestamp < template_data['first_seen']:
                template_data['first_seen'] = timestamp
            
            # Track platform sequence
            template_data['platform_sequence'].append((platform, timestamp))
        
        # Calculate momentum scores
        emerging_patterns = []
        for template_hash, data in template_activity.items():
            score = self._calculate_momentum_score(data)
            if score > 0.7:  # Threshold per "emerging"
                emerging_patterns.append({
                    'template_hash': template_hash,
                    'momentum_score': score,
                    'platforms': list(data['platforms']),
                    'cross_platform': len(data['platforms']) > 1,
                    'platform_sequence': self._analyze_platform_sequence(
                        data['platform_sequence']
                    ),
                    'prediction': self._predict_next_platform(data)
                })
        
        return sorted(emerging_patterns, 
                     key=lambda x: x['momentum_score'], reverse=True)
    
    def _calculate_momentum_score(self, template_data):
        """Calcola score basato su growth rate e cross-platform presence"""
        posts = template_data['posts']
        if len(posts) < 2:
            return 0
        
        # Time-weighted score growth
        now = datetime.now()
        total_score = 0
        time_penalty = 0
        
        for post in posts:
            age_hours = (now - post['timestamp']).total_seconds() / 3600
            # Newer posts get higher weight
            time_weight = math.exp(-age_hours / 24)  # Decay over 24h
            total_score += post['score'] * time_weight
            time_penalty += time_weight
        
        if time_penalty == 0:
            return 0
        
        avg_weighted_score = total_score / time_penalty
        
        # Cross-platform bonus
        platform_bonus = len(template_data['platforms']) * 0.3
        
        # Velocity bonus (posts frequency)
        time_span = (max(p['timestamp'] for p in posts) - 
                    min(p['timestamp'] for p in posts)).total_seconds() / 3600
        velocity_bonus = len(posts) / max(time_span, 1) if time_span > 0 else 0
        
        return min((avg_weighted_score / 1000) + platform_bonus + velocity_bonus, 5.0)
    
    def _analyze_platform_sequence(self, platform_sequence):
        """Analizza la sequenza di platform per identificare pattern"""
        sequence = sorted(platform_sequence, key=lambda x: x[1])
        platforms = [p[0] for p in sequence]
        
        # Common patterns
        if platforms == ['reddit', 'tiktok']:
            return "reddit_to_tiktok_migration"
        elif platforms == ['tiktok', 'instagram']:
            return "tiktok_to_instagram_expansion" 
        elif platforms == ['reddit', 'tiktok', 'instagram']:
            return "full_viral_sequence"
        else:
            return "custom_sequence"
    
    def _predict_next_platform(self, template_data):
        """Predici dove il meme apparirà successivamente"""
        current_platforms = template_data['platforms']
        
        # Simple rule-based prediction
        if 'reddit' in current_platforms and 'tiktok' not in current_platforms:
            return {'next_platform': 'tiktok', 'confidence': 0.7}
        elif 'tiktok' in current_platforms and 'instagram' not in current_platforms:
            return {'next_platform': 'instagram', 'confidence': 0.6}
        else:
            return {'next_platform': 'unknown', 'confidence': 0.1}

    def find_template_evolution(self, template_hash):
        """Traccia come un template evolve nel tempo"""
        query = """
        MATCH (p:MemePost {template_hash: $template_hash})
        RETURN p
        ORDER BY p.timestamp ASC
        """
        
        posts = self.db.run_query(query, template_hash=template_hash)
        
        evolution = {
            'original_post': posts[0] if posts else None,
            'variations': len(posts),
            'platforms_reached': len(set(p['platform'] for p in posts)),
            'peak_score': max(p['score'] for p in posts) if posts else 0,
            'lifecycle_stage': self._determine_lifecycle_stage(posts)
        }
        
        return evolution
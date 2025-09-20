# processors/image_analyzer.py
import imagehash
from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np

class ImageTemplateDetector:
    def __init__(self):
        self.hash_functions = {
            'phash': imagehash.phash,      # Structural similarity
            'dhash': imagehash.dhash,      # Gradient-based
            'whash': imagehash.whash,      # Wavelet hash
            'colorhash': imagehash.colorhash  # Color distribution
        }
    
    def extract_features(self, image_url):
        """Estrae multiple hash per robustezza"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert('RGB')
            
            features = {}
            for name, hash_func in self.hash_functions.items():
                features[name] = str(hash_func(image))
            
            # Template structure detection
            features['template_structure'] = self._detect_text_regions(image)
            
            return features
        except Exception as e:
            return None
    
    def _detect_text_regions(self, pil_image):
        """Detect text boxes positions - crude template detection"""
        # Convert PIL to OpenCV
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Find text regions with MSER
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Return normalized positions of text boxes
        h, w = gray.shape
        text_regions = []
        for region in regions:
            x, y, w_box, h_box = cv2.boundingRect(region.reshape(-1, 1, 2))
            text_regions.append({
                'x_norm': x/w, 'y_norm': y/h, 
                'w_norm': w_box/w, 'h_norm': h_box/h
            })
        
        return self._cluster_regions(text_regions)
    
    def _cluster_regions(self, regions):
        """Group nearby text regions - identifies template structure"""
        if len(regions) < 2:
            return "single_text" if regions else "no_text"
            
        # Simple clustering by vertical position
        top_regions = [r for r in regions if r['y_norm'] < 0.3]
        middle_regions = [r for r in regions if 0.3 <= r['y_norm'] <= 0.7]
        bottom_regions = [r for r in regions if r['y_norm'] > 0.7]
        
        structure = []
        if top_regions: structure.append('top')
        if middle_regions: structure.append('middle')  
        if bottom_regions: structure.append('bottom')
        
        return "_".join(structure) if structure else "scattered"

    def find_similar_templates(self, target_features, db_features, threshold=5):
        """Find templates with similar structure"""
        similar = []
        
        for db_item in db_features:
            similarity_score = 0
            
            # Compare hashes
            for hash_type in self.hash_functions.keys():
                if hash_type in target_features and hash_type in db_item:
                    hash1 = imagehash.hex_to_hash(target_features[hash_type])
                    hash2 = imagehash.hex_to_hash(db_item[hash_type])
                    similarity_score += (64 - (hash1 - hash2)) / 64
            
            # Template structure bonus
            if (target_features.get('template_structure') == 
                db_item.get('template_structure')):
                similarity_score += 1
            
            if similarity_score > threshold:
                similar.append({
                    'item': db_item,
                    'similarity': similarity_score
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)
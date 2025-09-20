# database/models.py
from py2neo import Graph, Node, Relationship

class MemePost(Node):
    def __init__(self, platform, post_id, title, score, timestamp, **kwargs):
        super().__init__("MemePost", 
                        platform=platform,
                        post_id=post_id, 
                        title=title,
                        score=score,
                        timestamp=timestamp,
                        **kwargs)

class MemeTemplate(Node):
    def __init__(self, template_hash, description, **kwargs):
        super().__init__("Template",
                        template_hash=template_hash,
                        description=description,
                        **kwargs)
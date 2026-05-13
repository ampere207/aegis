from qdrant_client import QdrantClient
from ..core.config import settings


class QdrantWrapper:
    def __init__(self):
        url = settings.QDRANT_URL
        if url:
            # basic client; collection management will be added later
            self.client = QdrantClient(url=url)
        else:
            self.client = None

    def ping(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

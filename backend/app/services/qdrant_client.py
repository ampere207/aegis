from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Qdrant vector database abstraction for semantic search."""

    def __init__(self):
        self.client: QdrantClient | None = None

    async def connect(self):
        """Initialize Qdrant connection."""
        if not settings.QDRANT_URL:
            logger.warning("Qdrant not configured")
            return
        try:
            self.client = QdrantClient(url=settings.QDRANT_URL)
            logger.info("Connected to Qdrant")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")

    async def create_collection(self, collection_name: str, vector_size: int = 1536):
        """Create or ensure vector collection exists."""
        if not self.client:
            return
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
        except Exception as e:
            logger.debug(f"Collection {collection_name} may already exist: {e}")

    async def upsert_vector(
        self, collection_name: str, point_id: int, vector: list, payload: dict
    ):
        """Insert or update a vector point."""
        if not self.client:
            return
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)],
            )
        except Exception as e:
            logger.error(f"Failed to upsert vector: {e}")

    async def search(self, collection_name: str, vector: list, limit: int = 10):
        """Search for similar vectors."""
        if not self.client:
            return []
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
            )
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


qdrant_store = QdrantVectorStore()

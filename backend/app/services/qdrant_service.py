"""Qdrant vector database service abstraction."""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for Qdrant vector storage.
    
    Phase 1: Stub implementation for future semantic embeddings.
    Will expand to support:
    - Code snippet embeddings
    - API specification embeddings
    - Vulnerability pattern embeddings
    - Semantic similarity search
    """
    
    _client: AsyncQdrantClient | None = None
    _collection_name = "aegis_vectors"

    @classmethod
    async def initialize(cls) -> None:
        """Initialize Qdrant connection on startup."""
        if settings.QDRANT_URL:
            try:
                cls._client = AsyncQdrantClient(url=settings.QDRANT_URL)
                # Ensure collection exists with 1536 dims (Gemini embedding size)
                collections = await cls._client.get_collections()
                exists = any(c.name == cls._collection_name for c in collections.collections)
                if not exists:
                    await cls._client.create_collection(
                        collection_name=cls._collection_name,
                        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                    )
                logger.info(f"Qdrant connected, collection '{cls._collection_name}' ready")
            except Exception as e:
                logger.error(f"Qdrant connection failed: {e}")

    @classmethod
    async def close(cls) -> None:
        """Close Qdrant connection on shutdown."""
        if cls._client:
            try:
                await cls._client.close()
            except Exception:
                pass

    @classmethod
    async def upsert_points(cls, points: list) -> None:
        """Bulk upsert points to Qdrant."""
        if not cls._client:
            return
        try:
            await cls._client.upsert(
                collection_name=cls._collection_name,
                points=points
            )
        except Exception as e:
            logger.error(f"Qdrant upsert failed: {e}")

    @classmethod
    async def upsert_vector(
        cls, 
        point_id: str | int, 
        vector: list[float], 
        payload: dict
    ) -> None:
        """Upsert a single vector with payload."""
        if not cls._client:
            return
        from qdrant_client.models import PointStruct
        point = PointStruct(id=point_id, vector=vector, payload=payload)
        await cls.upsert_points([point])

    @classmethod
    async def search(
        cls, 
        query_vector: list[float], 
        limit: int = 10
    ) -> list:
        """Search similar vectors. Phase 1: stub."""
        if not cls._client:
            return []
        # Placeholder
        return []

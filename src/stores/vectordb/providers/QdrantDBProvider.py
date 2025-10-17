from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_client: str, default_vector_size: int = 786,
                 distance_method: str = None, index_threshold: int = 100):

        self.client = None
        self.db_client = db_client
        self.distance_method = None
        self.default_vector_size = default_vector_size

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger('uvicorn')

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None

    async def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    async def list_all_collections(self) -> List:
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    async def delete_collection(self, collection_name: str):
        if await self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            result = self.client.delete_collection(collection_name=collection_name)
            return result
        return None

    async def create_collection(self, collection_name: str,
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            # Ensure deletion completes before creation
            _ = await self.delete_collection(collection_name=collection_name)

        if not await self.is_collection_existed(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")

            # qdrant-client is synchronous; do not await its methods
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True

        return False

    async def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None,
                         record_id: str = None):

        if not await self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True

    async def insert_many(self, collection_name: str, texts: list,
                          vectors: list, metadata: list = None,
                          record_ids: list = None, batch_size: int = 50):

        n = len(texts)

        if metadata is None:
            metadata = [None] * n

        if record_ids is None:
            record_ids = list(range(0, n))

        # upfront validation to fail fast with a clear message
        if not (len(vectors) == n and len(metadata) == n and len(record_ids) == n):
            raise ValueError(
                f"Length mismatch: texts={n}, vectors={len(vectors)}, "
                f"metadata={len(metadata)}, record_ids={len(record_ids)}"
            )

        self.logger.debug(
            "lens — texts:%d vectors:%d metadata:%d record_ids:%d",
            len(texts), len(vectors), len(metadata), len(record_ids)
        )

        for i in range(0, n, batch_size):
            batch_end = min(i + batch_size, n)

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [
                models.Record(
                    id=rid,
                    vector=vec,
                    payload={"text": txt, "metadata": meta}
                )
                for rid, vec, txt, meta in zip(
                    batch_record_ids, batch_vectors, batch_texts, batch_metadata
                )
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True

    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):

        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results) == 0:
            return None

        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],
            })
            for result in results
        ]


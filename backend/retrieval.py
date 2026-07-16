import numpy as np
import pandas as pd

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient, models

from config import (
    CSV_FILE,
    COLLECTION_NAME,
    QDRANT_URL,
    EMBEDDING_MODEL,
    EMBEDDING_DIM
)

BATCH_SIZE_EMBED = 32
BATCH_SIZE_QDRANT = 4096
PARALLEL_UPLOAD = 1


class RetrievalService:

    def __init__(self):

        self.client = QdrantClient(
            url=QDRANT_URL,
            prefer_grpc=True,
        )

        self.embedder = OllamaEmbeddings(
            model=EMBEDDING_MODEL
        )

        self.vector_store = self._initialize_vector_store()

    def _initialize_vector_store(self):

        collections = {
            c.name
            for c in self.client.get_collections().collections
        }

        if COLLECTION_NAME not in collections:

            print(f"Creating collection '{COLLECTION_NAME}'...")

            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
                hnsw_config=models.HnswConfigDiff(
                    m=0,
                    ef_construct=100,
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0,
                ),
            )

            total_docs = 0

            for chunk in pd.read_csv(
                CSV_FILE,
                usecols=["Title", "Review", "Rating", "Date"],
                chunksize=BATCH_SIZE_EMBED,
            ):

                texts = []
                payloads = []

                for row in chunk.itertuples(index=False):

                    title = str(row.Title).strip()
                    review = str(row.Review).strip()

                    if not title and not review:
                        continue

                    content = "\n".join(
                        [
                            f"Title: {title}",
                            f"Review: {review}",
                            f"Rating: {row.Rating}",
                            f"Date: {row.Date}",
                        ]
                    )

                    texts.append(content)

                    payloads.append(
                        {
                            "content": content,
                            "rating": int(row.Rating),
                            "date": str(row.Date),
                        }
                    )

                if not texts:
                    continue

                embeddings = np.asarray(
                    self.embedder.embed_documents(texts),
                    dtype=np.float32,
                )

                self.client.upload_collection(
                    collection_name=COLLECTION_NAME,
                    vectors=embeddings,
                    payload=payloads,
                    parallel=PARALLEL_UPLOAD,
                    batch_size=BATCH_SIZE_QDRANT,
                    # show_progress=False,
                )

                total_docs += len(texts)

                if total_docs % 1000 == 0:
                    print(f"Indexed {total_docs:,} documents")

            print(f"Finished indexing {total_docs:,} documents.")

            print("Building HNSW index...")

            self.client.update_collection(
                collection_name=COLLECTION_NAME,
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100,
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=20000,
                ),
            )

            print("Index complete.")

        else:
            print(f"Using existing collection '{COLLECTION_NAME}'")

        return QdrantVectorStore(
            client=self.client,
            collection_name=COLLECTION_NAME,
            embedding=self.embedder,
        )

    def retrieve(self, query: str, top_k: int = 5):

        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
        )

        matches = []

        for doc, score in results:

            matches.append(
                {
                    "content": doc.metadata.get(
                        "content",
                        doc.page_content,
                    ),
                    "metadata": {
                        k: v
                        for k, v in doc.metadata.items()
                        if k != "content"
                    },
                    "score": float(score),
                }
            )

        return {
            "query": query,
            "matches": matches,
        }

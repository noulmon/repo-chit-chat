import logging

import numpy as np
from minsearch import Index, VectorSearch

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self, embedding_model, chunks: list[dict], embeddings):
        self.embedding_model = embedding_model
        self.chunks = chunks
        self.embeddings = np.array(embeddings)

        # build indexes once
        self.index = Index(
            text_fields=["chunk", "title", "description", "filename"], keyword_fields=[]
        )
        self.index.fit(chunks)

        self.vindex = VectorSearch()
        self.vindex.fit(self.embeddings, chunks)
        logger.info(f"SearchEngine initialized with {len(chunks)} chunks")

    def text_search(self, query: str) -> list[dict]:
        return self.index.search(query)

    def vector_search(self, query: str, num_results: int = 10) -> list[dict]:
        q = self.embedding_model.encode(query)
        return self.vindex.search(q, num_results=num_results)

    def hybrid_search(self, query: str, num_results: int = 10) -> list[dict]:
        text_results = self.text_search(query)
        vector_results = self.vector_search(query, num_results=num_results)

        seen = set()
        combined_results = []
        for result in text_results + vector_results:
            key = (result["filename"], result["chunk"])
            if key not in seen:
                seen.add(key)
                combined_results.append(result)

        return combined_results

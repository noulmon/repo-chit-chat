import numpy as np
from minsearch import Index, VectorSearch


class SearchEngine:
    def __init__(self, embedding_model, chunks, embeddings):
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

    def text_search(self, query: str) -> list:
        return self.index.search(query)

    def vector_search(self, query: str) -> list:
        q = self.embedding_model.encode(query)
        return self.vindex.search(q, num_results=1)

    def hybrid_search(self, query: str) -> list:
        text_results = self.text_search(query)
        vector_results = self.vector_search(query)

        seen = set()
        combined_results = []
        for result in text_results + vector_results:
            # use a unique chunk identifier instead of filename
            key = (result["filename"], result["chunk"])
            if key not in seen:
                seen.add(key)
                combined_results.append(result)

        return combined_results

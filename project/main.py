from data_ingestion.pipeline import run_pipeline
from data_ingestion.chunker import DataChunker
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

from search.retriever import SearchEngine


def generate_embeddings(chunks):
    embeddings = []

    for chunk in tqdm(chunks):
        v = embedding_model.encode(chunk['chunk'])
        embeddings.append(v)

    return embeddings

if __name__ == "__main__":
    embedding_model = SentenceTransformer('multi-qa-distilbert-cos-v1')


    data = run_pipeline('evidentlyai', 'docs')
    chunker = DataChunker('sliding_window', size=2000, step=1000)
    sliding_window_chunks = chunker.generate_document_chunks(data)
    embeddings = generate_embeddings(sliding_window_chunks)
    search_engine = SearchEngine(embedding_model, sliding_window_chunks, embeddings)
    query = "what is Evidently?"
    results = search_engine.hybrid_search(query)
    print(results)





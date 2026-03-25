from data_ingestion.pipeline import run_pipeline
from data_ingestion.chunker import DataChunker


if __name__ == "__main__":
    data = run_pipeline('evidentlyai', 'docs')
    chunker = DataChunker('sliding_window', size=2000, step=1000)
    sliding_window_chunks = chunker.generate_document_chunks(data)
    simple_chunks = chunker.simple_chunk(data, 2000)
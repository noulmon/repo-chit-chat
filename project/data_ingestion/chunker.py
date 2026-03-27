import logging
import os
import re

from groq import Groq

logger = logging.getLogger(__name__)


class DataChunker:
    def __init__(self, chunk_type: str = "simple", **kwargs):
        self.chunk_type = getattr(self, f"{chunk_type}_chunk", None)
        if self.chunk_type is None:
            raise ValueError(f"Unsupported chunk type: {chunk_type}")
        self.chunk_kwargs = kwargs
        self._groq_client: Groq | None = None

    def simple_chunk(self, sequence: str, chunk_size: int) -> list[dict]:
        return [
            {"chunk": sequence[i : i + chunk_size]}
            for i in range(0, len(sequence), chunk_size)
        ]

    def sliding_window_chunk(self, sequence: str, size: int, step: int) -> list[dict]:
        if size <= 0 or step <= 0:
            raise ValueError("size and step must be positive")

        seq_len = len(sequence)
        chunks = []
        for i in range(0, seq_len, step):
            chunk = sequence[i : i + size]
            chunks.append({"start": i, "chunk": chunk})
            if i + size >= seq_len:
                break

        return chunks

    def paragraph_chunk(self, text: str) -> list[dict]:
        return [{"chunk": para.strip()} for para in text.split("\n\n") if para.strip()]

    def markdown_level_chunk(self, text: str, level: int = 2) -> list[dict]:
        """
        Split markdown text by a specific header level.

        :param text: Markdown text as a string
        :param level: Header level to split on
        :return: List of sections as dicts with a 'chunk' key
        """
        # This regex matches markdown headers
        # For level 2, it matches lines starting with "## "
        header_pattern = r"^(#{" + str(level) + r"} )(.+)$"
        pattern = re.compile(header_pattern, re.MULTILINE)

        # Split and keep the headers
        parts = pattern.split(text)

        sections = []
        for i in range(1, len(parts), 3):
            # We step by 3 because regex.split() with
            # capturing groups returns:
            # [before_match, group1, group2, after_match, ...]
            # here group1 is "## ", group2 is the header text
            header = parts[i] + parts[i + 1]  # "## " + "Title"
            header = header.strip()

            # Get the content after this header
            content = ""
            if i + 2 < len(parts):
                content = parts[i + 2].strip()

            section = f"{header}\n\n{content}" if content else header
            sections.append({"chunk": section})

        return sections

    def llm_chunk(self, prompt: str) -> list[dict]:
        if self._groq_client is None:
            self._groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        messages = [{"role": "user", "content": prompt}]
        response = self._groq_client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return [{"chunk": response.choices[0].message.content}]

    def generate_document_chunks(self, documents: list[dict]) -> list[dict]:
        document_chunks = []
        for doc in documents:
            doc_copy = doc.copy()
            doc_content = doc_copy.pop("content")
            chunks = self.chunk_type(doc_content, **self.chunk_kwargs)
            for chunk in chunks:
                chunk.update(doc_copy)
            document_chunks.extend(chunks)
        logger.info(f"Generated {len(document_chunks)} chunks from {len(documents)} documents")
        return document_chunks

import os
import re

from groq import Groq

class DataChunker:
    def __init__(self, chunk_type="simple", **kwargs):
        self.chunk_type = getattr(self, f"{chunk_type}_chunk", None)
        if self.chunk_type is None:
            raise ValueError(f"Unsupported chunk type: {chunk_type}")
        self.chunk_kwargs = kwargs


    def simple_chunk(self, sequence, chunk_size):

        return [sequence[char:char+chunk_size] for char in range(0, len(sequence), chunk_size)]
    
    def sliding_window_chunk(self, sequence, size, step):
        if size <= 0 or step <= 0:
            raise ValueError("size and step must be positive")

        seq_len = len(sequence)
        chunks = []
        for i in range(0, seq_len, step):
            chunk = sequence[i:i+size]
            chunks.append({'start': i, 'chunk': chunk})
            if i + size >= seq_len:
                break

        return chunks
    
    def paragraph_chunk(self, text):
        return [para.strip() for para in text.split('\n\n') if para.strip()]
    
    def markdown_level_chunk(self, text, level=2):
        """
        Split markdown text by a specific header level.
        
        :param text: Markdown text as a string
        :param level: Header level to split on
        :return: List of sections as strings
        """
        # This regex matches markdown headers
        # For level 2, it matches lines starting with "## "
        header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
        pattern = re.compile(header_pattern, re.MULTILINE)

        # Split and keep the headers
        parts = pattern.split(text)
        
        sections = []
        for i in range(1, len(parts), 3):
            # We step by 3 because regex.split() with
            # capturing groups returns:
            # [before_match, group1, group2, after_match, ...]
            # here group1 is "## ", group2 is the header text
            header = parts[i] + parts[i+1]  # "## " + "Title"
            header = header.strip()

            # Get the content after this header
            content = ""
            if i+2 < len(parts):
                content = parts[i+2].strip()

            if content:
                section = f'{header}\n\n{content}'
            else:
                section = header
            sections.append(section)
        
        return sections


    def llm_chunk(self, prompt, model=os.getenv("GROQ_MODEL")):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            messages=messages,
            model=model,
        )
        
        return response.choices[0].message.content
    
    def generate_document_chunks(self, document):
        doucument_chunks = []
        for doc in document:
            doc_copy = doc.copy()
            doc_content = doc_copy.pop('content')
            chunks = self.chunk_type(doc_content, **self.chunk_kwargs)
            for chunk in chunks:
                chunk.update(doc_copy)
            doucument_chunks.extend(chunks)
        return doucument_chunks

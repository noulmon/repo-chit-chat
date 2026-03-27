import io
import logging
import zipfile

import frontmatter

logger = logging.getLogger(__name__)


def parse_repo_zip(zip_bytes: bytes) -> list:
    repository_data = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for file_info in zf.infolist():
            filename = file_info.filename
            filename_lower = filename.lower()

            if not (filename_lower.endswith(".md") or filename_lower.endswith(".mdx")):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode("utf-8", errors="ignore")
                    post = frontmatter.loads(content)
                    data = post.to_dict()
                    data["filename"] = filename
                    repository_data.append(data)
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=True)
                continue

    return repository_data

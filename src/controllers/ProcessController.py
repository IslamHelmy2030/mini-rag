import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from models import ProcessingEnum
from typing import List, Optional
from langchain.docstore.document import Document
from dataclasses import dataclass
from .BaseController import BaseController
from .ProjectController import ProjectController


@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):

    def __init__(self, project_id: int):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()

        return None


    def process_file_content(self, file_content: list, file_id: str,
                             chunk_size: int = 100, overlap_size: int = 20):

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        # chunks = text_splitter.create_documents(
        #     file_content_texts,
        #     metadatas=file_content_metadata
        # )

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )

        return chunks


    # def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int,
    #                              splitter_tag: str = "\n"):
    #
    #     full_text = " ".join(texts)
    #
    #     # split by splitter_tag
    #     lines = [doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1]
    #
    #     chunks = []
    #     current_chunk = ""
    #
    #     for line in lines:
    #         current_chunk += line + splitter_tag
    #         if len(current_chunk) >= chunk_size:
    #             chunks.append(Document(
    #                 page_content=current_chunk.strip(),
    #                 metadata={}
    #             ))
    #
    #             current_chunk = ""
    #
    #     if len(current_chunk) >= 0:
    #         chunks.append(Document(
    #             page_content=current_chunk.strip(),
    #             metadata={}
    #         ))
    #
    #     return chunks

    def process_simpler_splitter(
            self,
            texts: List[str],
            metadatas: Optional[List[dict]],
            chunk_size: int,
            splitter_tag: str = "\n",
            keep_separator: bool = True,
    ) -> List[Document]:
        """
        Split each input text on `splitter_tag`, pack pieces into chunks of at most `chunk_size` characters,
        and preserve per-text metadata.

        Notes:
          - `chunk_size` is in characters.
          - Long pieces are further sliced to respect the limit.
        """

        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")

        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("texts and metadatas must have the same length")

        chunks: List[Document] = []

        def flush_chunk(buf: List[str], meta: dict):
            if not buf:
                return
            content = "".join(buf)
            if content:  # prevent empty trailing chunk
                chunks.append(Document(page_content=content, metadata=meta or {}))

        for idx, text in enumerate(texts):
            meta = (metadatas[idx] if metadatas is not None else {}) or {}

            # Split this text only (preserves per-source metadata)
            raw_pieces = text.split(splitter_tag) if splitter_tag else [text]
            pieces = [p.strip() for p in raw_pieces if p.strip() != ""]  # keep single chars

            buf: List[str] = []
            buf_len = 0
            sep = splitter_tag if (keep_separator and splitter_tag) else ""

            for piece in pieces:
                # Append separator to the piece when packing (except when splitting a long piece)
                unit = piece + sep

                # If the unit itself is longer than chunk_size, slice it
                start = 0
                while start < len(unit):
                    remaining = chunk_size - buf_len
                    # If buffer is empty and unit is huge, take a full slice
                    take = min(remaining, len(unit) - start)

                    if take == 0:
                        # buffer full; flush and continue
                        flush_chunk(buf, meta)
                        buf, buf_len = [], 0
                        continue

                    buf.append(unit[start:start + take])
                    buf_len += take
                    start += take

                    if buf_len >= chunk_size:
                        flush_chunk(buf, meta)
                        buf, buf_len = [], 0

            # Flush any remainder for this text
            flush_chunk(buf, meta)

        return chunks

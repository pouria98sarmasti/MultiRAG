import re

import docx2txt
from pypdf import PdfReader
import pandas as pd

from pathlib import Path
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.schema._admin import AdminUploadedDatasetType


from src.utils.logger import setup_logger

logger = setup_logger(__name__)




class DocumentService:
    
    def __init__(self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        ) -> None:

        self._recursive_character_text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _remove_markdown_links(self, markdown_text: str):
        # Remove inline links including text: [text](url)
        text_without_inline_links = re.sub(r'\[([^\]]+)\]\([^)]+\)', '', markdown_text)
        
        # Remove reference-style links including text: [text][id]
        text_without_ref_links = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', '', text_without_inline_links)
        
        # Remove reference link definitions: [id]: url
        text_without_definitions = re.sub(r'^\s*\[[^\]]+\]:\s+[^\s]+\s*$', '', text_without_ref_links, flags=re.MULTILINE)
        
        # Remove automatic/bare links: <http://example.com>
        text_without_auto_links = re.sub(r'<(https?://[^>]+)>', '', text_without_definitions)
        
        # Remove images
        text_without_images: str = re.sub(r'!\[.*?\]\(.*?\)(?:\{.*?\})?', '', text_without_auto_links)

        # Remove consecutive blank lines that might be created after link removal
        clean_text = re.sub(r'\n\s*\n\s*\n', '\n\n', text_without_images)

        
        return clean_text



    def _pdf_to_documents(self, file_content: bytes) -> list[Document]:

        # write content to a temporary file, so pypdf will be able to read it
        unique_name = uuid.uuid4()
        with open(f"{unique_name}.pdf", "wb") as f:
            _ = f.write(file_content)

        file_path = Path(f"{unique_name}.pdf")

        markdown_text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            markdown_text += page.extract_text()

        clean_markdown_text = self._remove_markdown_links(markdown_text)


        # delete temporary file
        reader.close()
        file_path.unlink()

        docs = self._recursive_character_text_splitter.create_documents(texts=[clean_markdown_text], metadatas=[{"answer": ""}])

        return docs


    def _docx_to_documents(self, file_content: bytes) -> list[Document]:

        # write content to a temporary file, so docx2txt will be able to read it
        unique_name = uuid.uuid4()
        with open(f"{unique_name}.docx", "wb") as f:
            _ = f.write(file_content)

        file_path = Path(f"{unique_name}.docx")

        markdown_text = docx2txt.process(file_path)

        clean_markdown_text = self._remove_markdown_links(markdown_text)

        # delete temporary file
        file_path.unlink()

        docs = self._recursive_character_text_splitter.create_documents(texts=[clean_markdown_text], metadatas=[{"answer": ""}])

        return docs


    def _csv_to_documents(self, file_content: bytes) -> list[Document]:


        # write content to a temporary file, so pandas will be able to read it
        unique_name = uuid.uuid4()
        with open(f"{unique_name}.csv", "wb") as f:
            _ = f.write(file_content)

        file_path = Path(f"{unique_name}.csv")
        
        df = pd.read_csv(file_path)

        # delete temporary file
        file_path.unlink()

        docs = []
        for row in df.itertuples(index=False):
            doc = Document(
                page_content=row.question,
                metadata={"answer": row.answer},
            )
            docs.append(doc)
        
        return docs

    def to_documents(self, file_content: bytes, file_format: AdminUploadedDatasetType):
        
        file_format = file_format.value

        if file_format == "pdf":
            docs = self._pdf_to_documents(file_content=file_content)
        elif file_format == "docx":
            docs = self._docx_to_documents(file_content=file_content)
        elif file_format == "csv":
            docs = self._csv_to_documents(file_content=file_content)
        else:
            raise ValueError(f"File format: {file_format} not supported.")

        return docs


document_service = DocumentService()
import os
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Protocol

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


class PDFUpload(Protocol):
    name: str

    def getvalue(self) -> bytes: ...


def _load_pdf_documents(pdf: PDFUpload | str | Path) -> tuple[list[Document], str]:
    if isinstance(pdf, (str, os.PathLike)):
        pdf_path = Path(pdf)
        docs = PyPDFLoader(pdf_path).load()
        source_name = pdf_path.name
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "uploaded.pdf"
            pdf_path.write_bytes(pdf.getvalue())
            docs = PyPDFLoader(pdf_path).load()
        source_name = Path(pdf.name).name

    for doc in docs:
        doc.metadata["source"] = source_name
    return docs, source_name


def embed_pdf(pdf: PDFUpload | str | Path) -> Chroma:
    # Data Ingestion
    print(">> Data Loading")
    docs, _ = _load_pdf_documents(pdf)
    print(">> Data Loaded")

    # Split Into Chunks
    print(">> Splitting Into Chunks")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    print(">> Splitting Successful")

    # Embed The Chunks
    print(">> Loading Embedding Model")
    pdf_embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(">> Embedding Model Loaded")

    # Vector Database
    persist_directory = os.path.join(
        PROJECT_ROOT, "embedding", "VectorDB"
    )

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print(">> Existing VectorStore Found")

        chroma_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=pdf_embedding
        )

        # Add new chunks to the existing VectorStore
        chroma_store.add_documents(
            documents=chunks,
            ids=[str(uuid.uuid4()) for _ in chunks]
        )

        print(">> New Chunks Added To Existing VectorStore")

    else:
        print(">> Creating New VectorStore")

        chroma_store = Chroma.from_documents(
            documents=chunks,
            embedding=pdf_embedding,
            ids=[str(uuid.uuid4()) for _ in chunks],
            persist_directory=persist_directory
        )

        print(">> New VectorStore Created")

    return chroma_store

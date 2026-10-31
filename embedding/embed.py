import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from agent.llm_pick import pick_llm
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


def embed_pdf(pdf):
    # Data Ingestion
    print(">> Data Loading")
    loader = PyPDFLoader(pdf)
    docs = loader.load()
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
    print(">> Embedding...")
    pdf_embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(">> Embedding Successful")

    # Load Into VectorDB
    print(">> Loading Into VectorStore")
    persist_directory = os.path.join(PROJECT_ROOT, "embedding", "VectorDB")

    chroma_store = Chroma.from_documents(
        documents=chunks,
        embedding=pdf_embedding,
        persist_directory=persist_directory
    )
    print(">> Loaded Into VectorStore")

    return chroma_store

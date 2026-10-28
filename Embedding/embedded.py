from langchain_openai import ChatOpenAI
from langchain_community.chromadb import ChromaDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

def embed(pdf:str):
    
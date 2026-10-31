import os
from agent.llm_pick import pick_llm
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def embed_pdf(pdf):
    #Data Injestion
    loader = PyPDFLoader(pdf)
    docs = loader.load()
    
    #Split Into Chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100
    )
    chunk = splitter.split_documents(docs)
    
    #Embedd The Chunks
    pdf_embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    #Load In VecorDB
    chroma_store = Chroma.from_documents(
        documents = chunk,
        embedding = pdf_embedding,
        persist_directory= "../embedding/VectorDB/"
    )
    
    return chroma_store

llm = pick_llm("high")

if __name__ == "__main__":
    vectorstore = embed_pdf(r"C:\Users\Samarth\Desktop\Projects\RAG-Based-PDF-ChatBot\data\63_TYAIA03_Experiment_NO_10(Rohit Lonkar).pdf")
    result = vectorstore.similarity_search("What Is The Name Of University")
    response = llm.invoke(result)
    print(response.content)
    
    
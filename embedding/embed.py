import os
# from agent.llm_pick import pick_llm
# from chromadb import ChromaDB

def embed_pdf(pdf,mode)->str:
    with open(pdf, "rb+") as f:
        f.readlines()
        return f

if __name__ == "__main__":
    print(embed_pdf("C:\\Users\\Samarth\\Desktop\\Projects\\RAG-Based-PDF-ChatBot\\data\\63_TYAIA03_Experiment_NO_10(Rohit Lonkar).pdf","rb+"))
    
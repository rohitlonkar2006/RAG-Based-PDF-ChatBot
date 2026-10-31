import streamlit as st
from agent.llm_pick import pick_llm
from embedding.embed import embed_pdf
from langchain_chroma import Chroma
st.title("PDF Analyzer ChatBot Using RAG")

prompt = st.chat_input(
    "Ask Something About Your PDFs",
    accept_file="multiple",
    file_type=["pdf"]
)

if prompt:
    pdfs = prompt.files
    text = prompt.text

    for pdf in pdfs:
        vectorstore = embed_pdf(pdf)

        result = vectorstore.similarity_search(text)

        llm = pick_llm("high")

        context = "\n\n".join(doc.page_content for doc in result)

        response = llm.invoke(
            f"Answer the question using the following context:\n{context}\n\n"
            f"Question: {text}"
        )

        st.write(response.content)
import streamlit as st
from agent.llm_pick import pick_llm
st.title("PDF Analyzer ChatBot Using RAG")

prompt = st.chat_input(
    "Ask Something About Your PDF's",
    accept_file = "multiple",
    file_type = ["pdf"]
)


    
        
    
import os

from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

if os.environ['GROQ_API_KEY']:
    print("API Loaded")
else:
    print("API Not Found")
    
def pick_llm(level:str):
    if level == "low":
        llm = ChatGroq(model = "openai/gpt-oss-20b",temperature=0)
    elif level == "medium":
        llm = ChatGroq(model = "openai/gpt-oss-120b",temperature=0.7)
    elif level == "high":
        llm = ChatGroq(model = "openai/gpt-oss-120b",temperature=1)
    else:
        raise ValueError("Wrong Choise Choose Between ('low','medium','high')")
    return llm

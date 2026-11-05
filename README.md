# PaperPilot — RAG-Based PDF Chatbot

PaperPilot is a Streamlit app for asking questions about PDF documents. It
indexes uploaded PDFs, retrieves relevant passages, and uses a Groq-hosted
language model to generate answers grounded in those passages.

## Features

- Upload one or more PDFs from the sidebar.
- Extract and chunk PDF text, then create embeddings with
  `sentence-transformers/all-MiniLM-L6-v2`.
- Store and search document chunks with Chroma.
- Ask follow-up questions in a persistent chat interface and see source
  document/page citations when available.
- Use a responsive dark interface with lightweight animations.

## Requirements

- Python 3.13 or newer
- A [Groq API key](https://console.groq.com/keys)
- [uv](https://docs.astral.sh/uv/) or pip

## Setup

Clone the repository and open its directory:

```powershell
git clone https://github.com/rohitlonkar2006/RAG-Based-PDF-ChatBot.git
cd RAG-Based-PDF-ChatBot
```

Install the project dependencies using uv:

```powershell
uv sync
```

Alternatively, install the project and its dependencies with pip:

```powershell
python -m pip install .
```

Create a `.env` file in the project root and add your Groq API key:

```text
GROQ_API_KEY=your_groq_api_key
```

Keep your API key private. Do not commit the `.env` file.

## Run the app

With uv:

```powershell
uv run streamlit run main.py
```

Or activate your virtual environment and run:

```powershell
streamlit run main.py
```

Open the local URL printed by Streamlit. Upload PDFs from **Your knowledge
base** in the sidebar, select **Add to knowledge base**, then ask a question in
the chat box.

## How it works

1. The app writes each uploaded PDF to a temporary file so the PDF loader can
   read it, then extracts its pages.
2. The extracted text is split into overlapping chunks and embedded.
3. Chunks are saved in the local Chroma database under `embedding/VectorDB`.
4. For each question, the app retrieves relevant chunks and sends them as
   context to the Groq model. The response includes source citations where
   available.

The temporary upload file is removed after extraction. The Chroma database is
persisted locally so it can be reused between app runs.

## Project layout

```text
.
├── agent/
│   └── llm_pick.py       # Groq chat model selection
├── data/                 # Example PDF documents
├── embedding/
│   └── embed.py          # PDF loading, chunking, embeddings, and Chroma
├── main.py               # Streamlit chat application
├── pyproject.toml        # Project metadata and dependencies
└── .env                  # Local API key (create this; do not commit)
```

## Troubleshooting

- **`GROQ_API_KEY` is missing:** Confirm `.env` is in the project root and
  contains `GROQ_API_KEY=...`, then restart Streamlit.
- **The app still reports that an uploaded object is not a valid file path:**
  Stop the running Streamlit process and start it again from this repository
  with `streamlit run main.py` so it loads the current upload-handling code.
- **Embedding model download or initialization fails:** Check your internet
  connection; the Hugging Face sentence-transformer model is downloaded when
  first needed.

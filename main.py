from typing import Literal, TypedDict, cast

import streamlit as st
from agent.llm_pick import pick_llm
from embedding.embed import embed_pdf
from langchain_chroma import Chroma


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
    sources: list[str]

st.set_page_config(
    page_title="PaperPilot | PDF assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #e9edf8;
        --muted: #9aa6bd;
        --line: rgba(167, 183, 215, .13);
        --accent: #9b8cff;
        --mint: #78e4c2;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 68% 0%, rgba(87, 67, 174, .16), transparent 35%),
            #0b0e16;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: rgba(15, 19, 30, .96);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .block-container { max-width: 980px; padding-top: 2rem; padding-bottom: 5rem; }
    .brand {
        display: flex; align-items: center; gap: .75rem; margin-bottom: 2.4rem;
        color: var(--ink); font-size: 1.08rem; font-weight: 700; letter-spacing: -.03em;
    }
    .brand-mark {
        display: grid; place-items: center; width: 2.35rem; height: 2.35rem;
        border: 1px solid rgba(181, 168, 255, .35); border-radius: .8rem;
        color: #c9c0ff; background: linear-gradient(145deg, #30294e, #191b2c);
        box-shadow: 0 0 24px rgba(139, 119, 255, .16);
    }
    .eyebrow {
        color: var(--mint); font-size: .72rem; font-weight: 700;
        letter-spacing: .16em; text-transform: uppercase;
    }
    .hero-title {
        margin: .55rem 0 .4rem; color: var(--ink); font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 700; letter-spacing: -.055em; line-height: 1.12;
        animation: rise-in .55s ease both;
    }
    .hero-copy { color: var(--muted); font-size: 1rem; margin-bottom: 1.65rem; }
    .status-pill {
        display: inline-flex; align-items: center; gap: .5rem; padding: .38rem .72rem;
        border: 1px solid var(--line); border-radius: 999px;
        background: rgba(255,255,255,.025); color: var(--muted); font-size: .78rem;
    }
    .status-dot {
        width: .45rem; height: .45rem; border-radius: 50%; background: var(--mint);
        box-shadow: 0 0 12px rgba(120, 228, 194, .8); animation: breathe 2s ease-in-out infinite;
    }
    .welcome-card {
        margin: 3rem auto 1rem; max-width: 640px; padding: 2.2rem;
        border: 1px solid var(--line); border-radius: 1.25rem;
        background: linear-gradient(145deg, rgba(24, 29, 44, .9), rgba(17, 20, 31, .75));
        box-shadow: 0 22px 80px rgba(0,0,0,.2); text-align: center;
        animation: rise-in .7s ease both;
    }
    .welcome-icon {
        display: grid; place-items: center; width: 3.2rem; height: 3.2rem;
        margin: 0 auto 1rem; border: 1px solid rgba(155,140,255,.28);
        border-radius: 1.05rem; background: rgba(155,140,255,.1); font-size: 1.45rem;
    }
    .welcome-card h3 { margin: 0 0 .5rem; color: var(--ink); font-size: 1.25rem; }
    .welcome-card p { margin: 0; color: var(--muted); line-height: 1.7; }
    [data-testid="stChatMessage"] {
        border: 1px solid var(--line); border-radius: 1rem;
        background: rgba(20, 24, 37, .72); animation: rise-in .32s ease both;
    }
    [data-testid="stChatInput"] {
        border-color: rgba(155, 140, 255, .3); background: rgba(18, 22, 34, .94);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent); box-shadow: 0 0 0 3px rgba(155,140,255,.12);
    }
    div.stButton > button {
        border: 1px solid rgba(155,140,255,.34); border-radius: .75rem;
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px); border-color: var(--accent);
        box-shadow: 0 8px 24px rgba(111,91,224,.18);
    }
    @keyframes rise-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes breathe {
        0%, 100% { opacity: .65; transform: scale(.9); }
        50% { opacity: 1; transform: scale(1.12); }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

messages = cast(
    list[ChatMessage],
    st.session_state.setdefault("messages", []),
)
vectorstore = cast(
    Chroma | None,
    st.session_state.setdefault("vectorstore", None),
)
indexed_files = cast(
    list[str],
    st.session_state.setdefault("indexed_files", []),
)

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✦</span> PaperPilot</div>',
        unsafe_allow_html=True,
    )
    st.markdown("#### Your knowledge base")
    st.caption("Add PDFs and chat with the information inside them.")
    uploaded_pdfs = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF documents to add to your knowledge base.",
    )

    if st.button(
        "＋  Add to knowledge base",
        type="primary",
        disabled=not uploaded_pdfs,
        width="stretch",
    ):
        with st.spinner("Reading and indexing your PDFs…"):
            for pdf in uploaded_pdfs:
                vectorstore = embed_pdf(pdf)
                st.session_state.vectorstore = vectorstore
                if pdf.name not in indexed_files:
                    indexed_files.append(pdf.name)
        st.success(f"Ready to chat with {len(indexed_files)} PDF(s).")

    st.divider()
    st.markdown("##### Library")
    if indexed_files:
        for file_name in indexed_files:
            st.markdown(f"📄 `{file_name}`")
    else:
        st.caption("Your uploaded documents will appear here.")

    st.divider()
    st.markdown(
        '<div class="status-pill"><span class="status-dot"></span> '
        + ("Knowledge base ready" if vectorstore else "Waiting for your first PDF")
        + "</div>",
        unsafe_allow_html=True,
    )

st.markdown('<div class="eyebrow">YOUR PERSONAL PDF ASSISTANT</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">A little less searching.<br>A lot more understanding.</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-copy">Ask questions across your documents and get answers grounded in their content.</p>',
    unsafe_allow_html=True,
)

if not messages and not vectorstore:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-icon">✧</div>
            <h3>Your documents, in conversation.</h3>
            <p>Upload one or more PDFs in the sidebar, add them to your knowledge base,
            then ask a question here. PaperPilot will find the relevant passages
            and help you make sense of them.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["sources"]:
            st.caption("Sources: " + " · ".join(message["sources"]))

prompt = st.chat_input(
    "Ask anything about your documents…",
    disabled=vectorstore is None,
)

if prompt:
    messages.append({"role": "user", "content": prompt, "sources": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    if vectorstore is None:
        st.info("Add a PDF to your knowledge base before asking a question.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Searching your documents…"):
                documents = vectorstore.similarity_search(prompt, k=4)
                context = "\n\n".join(document.page_content for document in documents)
                llm = pick_llm("high")
                response = llm.invoke(
                    "Answer the question using only the following document context. "
                    "If the answer is not in the context, say so clearly.\n\n"
                    f"Context:\n{context}\n\nQuestion: {prompt}"
                )
                answer = str(response.content)
                sources: list[str] = []
                for document in documents:
                    source = str(document.metadata.get("source", "PDF"))
                    page = document.metadata.get("page")
                    citation = f"{source} · p. {page + 1}" if isinstance(page, int) else source
                    if citation not in sources:
                        sources.append(citation)

            st.markdown(answer)
            if sources:
                st.caption("Sources: " + " · ".join(sources))

        messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
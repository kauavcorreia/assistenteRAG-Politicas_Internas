from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS


VECTORSTORE_PATH = Path("app/data/vectorstore")


def load_vectorstore():
    embedding = OllamaEmbeddings(
        model="bge-m3",
        base_url="http://host.docker.internal:11434"
    )

    if not (VECTORSTORE_PATH / "index.faiss").exists():
        raise FileNotFoundError(
            "Vectorstore não encontrado. Execute "
            "'python -m app.rag.build_vectorstore' primeiro."
        )

    return FAISS.load_local(
        VECTORSTORE_PATH,
        embedding,
        allow_dangerous_deserialization=True
    )


vectorstore = load_vectorstore()
retriever = vectorstore.as_retriever()
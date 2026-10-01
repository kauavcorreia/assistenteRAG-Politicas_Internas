from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from app.rag.splitter import blocks

VECTORSTORE_PATH = Path("app/data/vectorstore")

def build_vectorstore():
    print(f"Gerando embeddings para {len(blocks)} blocos...")

    embedding = OllamaEmbeddings(
    model="bge-m3",
    base_url="http://localhost:11434")


    if (VECTORSTORE_PATH / "index.faiss").exists():
        return FAISS.load_local(
            VECTORSTORE_PATH,
            embedding,
            allow_dangerous_deserialization=True
        )
    
    vectorstore = FAISS.from_documents(blocks,embedding)

    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)

    print("Vectorstore criado com sucesso!")

if __name__ == "__main__":
    build_vectorstore()


 



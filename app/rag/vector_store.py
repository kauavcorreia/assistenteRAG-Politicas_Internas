from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from app.rag.splitter import blocks


def create_vectorstore(blocks):
    embedding = OllamaEmbeddings(model="bge-m3")
    vectorstore = FAISS.from_documents(blocks,embedding)
    return vectorstore

vectorstore = create_vectorstore(blocks)
retriever = vectorstore.as_retriever()
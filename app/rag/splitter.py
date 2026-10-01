from app.rag.loader import document
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

def block_splitter(document):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    blocks = splitter.split_documents(document)
    return blocks

blocks = block_splitter(document)
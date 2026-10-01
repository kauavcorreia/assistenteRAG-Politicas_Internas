import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
st.title("Assistente RAG — Políticas Internas")

#LÓGICA DO RAG
def load_pdf():
    pdf_loader = PyPDFLoader("politica_rh.pdf")
    text = pdf_loader.load()
    return text

document = load_pdf()


def block_splitter(document):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    blocks = splitter.split_documents(document)
    return blocks

blocks = block_splitter(document)


#EMBEDDING 
def create_vectorstore(blocks):
    embedding = OllamaEmbeddings(model="bge-m3")
    vectorstore = FAISS.from_documents(blocks,embedding)
    return vectorstore

vectorstore = create_vectorstore(blocks)
retriever = vectorstore.as_retriever()

#LÓGICA DO AGENTE DE IA
@st.cache_resource
def create_chain(vectorstore):

    system_prompt = ChatPromptTemplate.from_template("""Você é um assistente de RH que responde perguntas sobre as
    políticas internas da empresa. use APENAS as informações do context abaixo para responder.
    Se não encontrar a resposta, diga claramente que não sabe responder.
    Responda em português do Brasil, de forma clara e objetiva.
    contexto:{context}
    pergunta: {answer} 
    resposta: """)

    context_retriever = retriever
    llm = ChatOllama(
    model="qwen2.5:0.5b")

    chain = ({"context": context_retriever, "question": RunnablePassthrough()} 
             | system_prompt    
             | llm
             | StrOutputParser())


    return chain

# INTERFACE


# carregar chain e vector store
chain = create_chain()
# armazena em uma lista as mensagens enviadas pelo usuario em uma session(cookies)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# exibe as mensagens na tela
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Pergunte sobre as políticas da empresa...")
if prompt :
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando..."):
            answer = chain.invoke(prompt)
            st.write(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
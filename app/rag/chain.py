from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from app.rag.vector_store import retriever


def create_chain():
    system_prompt = ChatPromptTemplate.from_template("""Você é um assistente de RH que responde perguntas sobre as
    políticas internas da empresa. use APENAS as informações do context abaixo para responder.
    Se não encontrar a resposta, diga claramente que não sabe responder.
    Responda em português do Brasil, de forma clara e objetiva.
    contexto:{context}
    pergunta: {question} 
    resposta: """)

    context_retriever = retriever
    llm = ChatOllama(
    model="qwen2.5:0.5b")

    chain = ({"context": context_retriever, "question": RunnablePassthrough()} 
             | system_prompt    
             | llm
             | StrOutputParser())


    return chain

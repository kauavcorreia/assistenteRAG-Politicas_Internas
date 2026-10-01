from fastapi import APIRouter, status
from app.api.dto.message_dto import Message
from app.rag.chain import create_chain

router = APIRouter()

@router.post("/chat", status_code=status.HTTP_200_OK)
def process_message(data: Message):
    chain = create_chain()
    response = chain.invoke(data.message)
    return {"response": response}


    

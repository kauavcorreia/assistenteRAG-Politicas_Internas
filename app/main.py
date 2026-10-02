from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.whatsapp import router as whatsapp_router


app = FastAPI()

app.include_router(chat_router)
app.include_router(whatsapp_router, prefix="/api")



            





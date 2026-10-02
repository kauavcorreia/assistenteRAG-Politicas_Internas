import os
from typing import Any

import requests
from fastapi import APIRouter, status

from app.rag.chain import create_chain

router = APIRouter()

WAHA_URL = os.getenv("WAHA_URL", "http://waha:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def whatsapp_webhook(data: dict[str, Any]):
    print("Evento recebido do WAHA:")
    print(data)

    if data.get("event") != "message.any":
        return {"success": True}

    payload = data.get("payload", {})

    if payload.get("fromMe"):
        print("Mensagem enviada pelo próprio bot. Ignorando.")
        return {"success": True}

    message = payload.get("body")
    chat_id = payload.get("from")

    if not message or not chat_id:
        return {"success": True}

    print(f"Mensagem recebida: {message}")
    print(f"Chat ID: {chat_id}")

    chain = create_chain()
    response = chain.invoke(message)

    send_message(chatid=chat_id, text=response)

    return {"success": True}


def send_message(chatid: str, text: str):
    url = f"{WAHA_URL}/api/sendText"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Api-Key": WAHA_API_KEY
    }

    data = {
        "chatId": chatid,
        "text": text,
        "session": "default"
    }

    response = requests.post(
        url,
        json=data,
        headers=headers,
    )

    response.raise_for_status()

    return response.json()

    




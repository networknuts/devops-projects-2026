import os
import uuid
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from app.database import get_db_cursor
from app.models import ChatRequest, ChatResponse, ConversationDetail, Message
from app.schema import initialize_schema

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="AI Question Answering API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    initialize_schema()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    conversation_id = payload.conversation_id or str(uuid.uuid4())
    user_message_id = str(uuid.uuid4())
    assistant_message_id = str(uuid.uuid4())

    with get_db_cursor(commit=False) as cur:
        cur.execute(
            "SELECT message_text, role FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
            (conversation_id,),
        )
        history_rows = cur.fetchall()

    messages: List[dict] = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Answer clearly and accurately.",
        }
    ]
    for message_text, role in history_rows:
        messages.append({"role": role, "content": message_text})
    messages.append({"role": "user", "content": question})

    try:
        response = client.responses.create(model=OPENAI_MODEL, input=messages)
        answer = response.output_text.strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    title = question[:80]
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO conversations (id, title)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (conversation_id, title),
        )
        cur.execute(
            """
            INSERT INTO messages (id, conversation_id, role, message_text)
            VALUES (%s, %s, 'user', %s)
            """,
            (user_message_id, conversation_id, question),
        )
        cur.execute(
            """
            INSERT INTO messages (id, conversation_id, role, message_text)
            VALUES (%s, %s, 'assistant', %s)
            """,
            (assistant_message_id, conversation_id, answer),
        )

    return ChatResponse(conversation_id=conversation_id, answer=answer)


@app.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str) -> ConversationDetail:
    with get_db_cursor(commit=False) as cur:
        cur.execute(
            "SELECT id, title FROM conversations WHERE id = %s",
            (conversation_id,),
        )
        conversation_row = cur.fetchone()
        if not conversation_row:
            raise HTTPException(status_code=404, detail="Conversation not found")

        cur.execute(
            """
            SELECT id, conversation_id, role, message_text, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        )
        message_rows = cur.fetchall()

    messages = [
        Message(
            id=str(row[0]),
            conversation_id=str(row[1]),
            role=row[2],
            message_text=row[3],
            created_at=row[4].isoformat(),
        )
        for row in message_rows
    ]

    return ConversationDetail(
        conversation_id=str(conversation_row[0]),
        title=conversation_row[1],
        messages=messages,
    )

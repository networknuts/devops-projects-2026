import os
import uuid
import time
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from app.database import get_db_cursor
from app.models import ChatRequest, ChatResponse, ConversationDetail, Message
from app.schema import initialize_schema

load_dotenv()

# -----------------------
# Env Config
# -----------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------
# FastAPI App
# -----------------------

app = FastAPI(title="AI Question Answering API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Prometheus Metrics
# -----------------------

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
)

IN_PROGRESS = Gauge(
    "app_inprogress_requests",
    "Number of in-progress requests",
)

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total chat requests",
)

CHAT_ERRORS = Counter(
    "chat_errors_total",
    "Total chat errors",
)

TOKENS_TOTAL = Counter(
    "openai_tokens_total",
    "Total tokens used",
    ["type"],  # input | output | total
)

# -----------------------
# Middleware
# -----------------------

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    IN_PROGRESS.inc()

    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=request.url.path,
        ).observe(duration)

        IN_PROGRESS.dec()

# -----------------------
# Startup
# -----------------------

@app.on_event("startup")
def startup_event() -> None:
    initialize_schema()

# -----------------------
# Health Endpoint
# -----------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

# -----------------------
# Metrics Endpoint
# -----------------------

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

# -----------------------
# Chat Endpoint
# -----------------------

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    conversation_id = payload.conversation_id or str(uuid.uuid4())
    user_message_id = str(uuid.uuid4())
    assistant_message_id = str(uuid.uuid4())

    # -----------------------
    # Load History
    # -----------------------

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

    # -----------------------
    # OpenAI Call
    # -----------------------

    CHAT_REQUESTS.inc()

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=messages,
        )

        answer = response.output_text.strip()

        # -----------------------
        # Token Metrics
        # -----------------------

        if hasattr(response, "usage") and response.usage:
            usage = response.usage

            input_tokens = getattr(usage, "input_tokens", 0)
            output_tokens = getattr(usage, "output_tokens", 0)
            total_tokens = getattr(usage, "total_tokens", 0)

            TOKENS_TOTAL.labels(type="input").inc(input_tokens)
            TOKENS_TOTAL.labels(type="output").inc(output_tokens)
            TOKENS_TOTAL.labels(type="total").inc(total_tokens)

    except Exception as exc:
        CHAT_ERRORS.inc()
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI request failed: {exc}",
        ) from exc

    # -----------------------
    # Save to DB
    # -----------------------

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

    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer,
    )

# -----------------------
# Get Conversation
# -----------------------

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

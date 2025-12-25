from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from llm import UniversalLLM
import psycopg2
from auth import get_current_user
from crypto import encrypt
from db import get_internal_db_connection
from fastapi.middleware.cors import CORSMiddleware

from semantic_storage import validate_semantic_plan
from sql_builder import build_sql_from_plan
from sql_validator import validate_sql
from limit_enforcer import enforce_row_limit
from schema import QueryRequest
from db import get_user_database_credentials
from answer_generator import generate_answer

# ---------------------------------
# App Initialization
# ---------------------------------
app = FastAPI(
    title="WhareIQ API",
    description="Semantic SQL & Data Warehouse Intelligence Engine",
    version="v1"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------
# Request / Response Models
# ---------------------------------
class PlanRequest(BaseModel):
    question: str


class PlanResponse(BaseModel):
    needs_clarification: bool
    clarification_question: str | None = None
    plan: dict | None = None

class DatabaseConnectRequest(BaseModel):
    host: str
    port: int
    db_name: str
    username: str
    password: str


# ---------------------------------
# Load Planner Prompt
# ---------------------------------
with open("specs/planner_prompt.txt", "r") as f:
    PLANNER_PROMPT = f.read()

# ---------------------------------
# Init Universal LLM
# ---------------------------------
llm = UniversalLLM(provider="groq")


# ---------------------------------
# Health Check
# ---------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "WhareIQ API"}


# ---------------------------------
# /plan Endpoint
# ---------------------------------
@app.post("/plan", response_model=PlanResponse)
def generate_plan(payload: PlanRequest):
    try:
        plan_json = llm.generate_json(
            system_prompt=PLANNER_PROMPT,
            user_input=payload.question,
        )
    except ValueError as e:
        # LLM / schema-related issues – bad request from semantic layer
        raise HTTPException(
            status_code=400,
            detail=f"Plan generation failed: {str(e)}",
        )
    except Exception as e:
        # Unexpected internal errors
        raise HTTPException(
            status_code=500,
            detail=f"Plan generation failed: {str(e)}",
        )

    # -----------------------------
    # Clarification Fallback Logic
    # -----------------------------
    if plan_json.get("needs_clarification") is True:
        return {
            "needs_clarification": True,
            "clarification_question": plan_json.get("clarification_question"),
            "plan": None,
        }

    # -----------------------------
    # Confidence Safety Check
    # -----------------------------
    confidence = plan_json.get("plan", {}).get("confidence_level")

    if confidence == "low":
        return {
            "needs_clarification": True,
            "clarification_question": "Your question is ambiguous. Please provide more details.",
            "plan": None,
        }

    # -----------------------------
    # Normal Safe Return
    # -----------------------------
    return plan_json

@app.post("/connect-database")
def connect_database(
    payload: DatabaseConnectRequest,
    user: dict = Depends(get_current_user)  # ✅ FIX 1
):
    user_id = user["id"]  # ✅ FIX 2

    # 1. Test connection to user's DB
    try:
        conn = psycopg2.connect(
            host=payload.host,
            port=payload.port,
            dbname=payload.db_name,
            user=payload.username,
            password=payload.password,
            connect_timeout=5
        )
        conn.close()
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot connect to database")

    # 2. Store encrypted credentials
    internal_conn = get_internal_db_connection()
    cur = internal_conn.cursor()

    cur.execute("""
        INSERT INTO user_database
        (user_id, host, port, db_name, username, encrypted_password)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET
          host = EXCLUDED.host,
          port = EXCLUDED.port,
          db_name = EXCLUDED.db_name,
          username = EXCLUDED.username,
          encrypted_password = EXCLUDED.encrypted_password;
    """, (
        user_id,                      # ✅ now a UUID string
        payload.host,
        payload.port,
        payload.db_name,
        payload.username,
        encrypt(payload.password)
    ))

    internal_conn.commit()
    cur.close()
    internal_conn.close()

    return {"status": "connected"}


@app.post("/query")
def query_data(
    payload: QueryRequest,
    user: dict = Depends(get_current_user)
):
    user_id = user["id"]

    # 1️⃣ Load user's DB credentials
    db_creds = get_user_database_credentials(user_id)
    if not db_creds:
        raise HTTPException(
            status_code=400,
            detail="No database connected for this user"
        )

    # 2️⃣ Generate semantic plan using LLM
    llm = UniversalLLM()
    semantic_plan = llm.generate_plan(payload.question)

    # 3️⃣ Validate semantic plan schema
    validate_semantic_plan(semantic_plan)

    # 4️⃣ Resolve semantic plan → SQL
    sql = build_sql_from_plan(semantic_plan)

    # 5️⃣ Enforce SQL safety
    validate_sql(sql)
    sql = enforce_row_limit(sql)

    # 6️⃣ Execute SQL on USER database
    try:
        conn = psycopg2.connect(
            host=db_creds["host"],
            port=db_creds["port"],
            dbname=db_creds["db_name"],
            user=db_creds["username"],
            password=db_creds["password"],
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 7️⃣ Human summary (V1: simple deterministic)
    answer = generate_answer(semantic_plan, rows)

    return {
        "answer": answer,
        "sql": sql,
        "rows": rows
    }

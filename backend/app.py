from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from llm import UniversalLLM
import psycopg2
from auth import get_current_user
from crypto import encrypt
from db import get_internal_db_connection

# ---------------------------------
# App Initialization
# ---------------------------------
app = FastAPI(
    title="WhareIQ API",
    description="Semantic SQL & Data Warehouse Intelligence Engine",
    version="v1"
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

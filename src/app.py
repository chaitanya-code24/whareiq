from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.llm import UniversalLLM

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
            user_input=payload.question
        )

        # -----------------------------
        # Clarification Fallback Logic
        # -----------------------------
        if plan_json.get("needs_clarification") is True:
            return {
                "needs_clarification": True,
                "clarification_question": plan_json.get("clarification_question"),
                "plan": None
            }

        # -----------------------------
        # Confidence Safety Check
        # -----------------------------
        confidence = plan_json.get("plan", {}).get("confidence_level")

        if confidence == "low":
            return {
                "needs_clarification": True,
                "clarification_question": "Your question is ambiguous. Please provide more details.",
                "plan": None
            }

        # -----------------------------
        # Normal Safe Return
        # -----------------------------
        return plan_json

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plan generation failed: {str(e)}"
        )

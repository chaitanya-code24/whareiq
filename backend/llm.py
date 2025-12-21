from groq import Groq
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from jsonschema import validate, ValidationError

# ---------------------------------
# Load Environment Variables
# ---------------------------------
load_dotenv()

# ---------------------------------
# Load Semantic Plan JSON Schema
# ---------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT_DIR / "backend" / "specs" / "semantic_plan.schema.json"

with open(SCHEMA_PATH, "r") as f:
    SEMANTIC_PLAN_SCHEMA = json.load(f)


# ---------------------------------
# Universal LLM Client
# ---------------------------------
class UniversalLLM:
    def __init__(self, provider: str = "groq"):
        self.provider = provider
        self.client = self._init_client()

    def _init_client(self):
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")

            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")

            return Groq(api_key=api_key)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _safe_json_load(self, raw_output: str) -> dict:
        """
        Parse LLM output as JSON. Raise a clean error if invalid.
        """
        try:
            return json.loads(raw_output)
        except Exception as e:
            raise ValueError(f"LLM returned invalid JSON: {str(e)}")

    def _validate_against_schema(self, plan: dict) -> dict:
        """
        Validate the parsed JSON against the WhareIQ semantic plan schema.
        """
        try:
            validate(instance=plan, schema=SEMANTIC_PLAN_SCHEMA)
        except ValidationError as e:
            raise ValueError(
                f"Semantic plan does not match schema: {e.message}"
            )

        return plan

    def generate_json(
        self,
        system_prompt: str,
        user_input: str,
        model: str = "llama3-8b-8192",
    ) -> dict:
        """
        Generate a semantic plan JSON using the LLM, then validate it.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {str(e)}")

        raw_output = completion.choices[0].message.content

        parsed = self._safe_json_load(raw_output)
        validated = self._validate_against_schema(parsed)

        return validated

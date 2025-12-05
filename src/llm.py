from groq import Groq
import os
import json
from dotenv import load_dotenv

# ---------------------------------
# Load Environment Variables
# ---------------------------------
load_dotenv()

# ---------------------------------
# Universal LLM Client
# ---------------------------------
class UniversalLLM:
    def __init__(self, provider="groq"):
        self.provider = provider
        self.client = self._init_client()

    def _init_client(self):
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")

            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")

            return Groq(api_key=api_key)

        raise ValueError("Unsupported LLM provider")

    def generate_json(self, system_prompt: str, user_input: str, model="llama3-8b-8192"):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )

        raw_output = completion.choices[0].message.content

        return json.loads(raw_output)

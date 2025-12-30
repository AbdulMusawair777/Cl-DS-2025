from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import language_tool_python
from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================
# Load environment variables
# =========================
load_dotenv()

# =========================
# FastAPI app
# =========================
app = FastAPI(title="Grammar Coach Bot with LLM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Static & Templates
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()

# =========================
# LanguageTool (local)
# =========================
try:
    tool = language_tool_python.LanguageTool("en-US")
except Exception as e:
    tool = None
    print("LanguageTool failed:", e)

# =========================
# OpenAI (optional)
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

print("OPENAI ENABLED:", bool(client))

# =========================
# Request model
# =========================
class GrammarRequest(BaseModel):
    text: str

# =========================
# LLM explanation (safe)
# =========================
def get_llm_explanation(original: str, corrected: str) -> str:
    if not client:
        return "Grammar corrected using rule-based analysis."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful grammar teacher."},
                {
                    "role": "user",
                    "content": f"""
Explain the grammar mistakes simply.

Original:
{original}

Corrected:
{corrected}
"""
                }
            ],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Explanation unavailable (LLM error)."

# =========================
# API endpoint
# =========================
@app.post("/check-grammar")
def check_grammar(request: GrammarRequest):
    if not tool:
        raise HTTPException(status_code=500, detail="Grammar engine not available")

    matches = tool.check(request.text)
    corrected = language_tool_python.utils.correct(request.text, matches)

    if request.text.strip() == corrected.strip():
        explanation = "Your sentence is already grammatically correct. Well done!"
    else:
        explanation = get_llm_explanation(request.text, corrected)

    return {
        "corrected_text": corrected,
        "explanation": explanation
    }

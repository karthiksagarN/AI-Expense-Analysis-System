import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List
from dotenv import load_dotenv
import itertools
import asyncio

# --- Load environment variables ---
load_dotenv()
API_KEYS = os.getenv("GEMINI_API_KEYS")

if not API_KEYS:
    raise ValueError("❌ GEMINI_API_KEYS not found. Please set it in your .env file.")

API_KEYS = [k.strip() for k in API_KEYS.split(",") if k.strip()]
if not API_KEYS:
    raise ValueError("❌ No valid API keys found.")

# Round-robin iterator for rotating keys
api_key_cycle = itertools.cycle(API_KEYS)

# --- Helper: dynamic Gemini configuration ---
def get_genai_model(model_name: str, system_instruction: str, schema=None):
    api_key = next(api_key_cycle)
    genai.configure(api_key=api_key)
    print(f"🔄 Using API key: {api_key[:6]}...")

    config = {
        "model_name": model_name,
        "system_instruction": system_instruction,
        "generation_config": {"response_mime_type": "application/json"},
    }

    if schema:
        config["generation_config"]["response_schema"] = schema

    return genai.GenerativeModel(**config)


# ----------------------------------------------------------------------
# 🧠 AGENT 1: Transaction Categorization
# ----------------------------------------------------------------------

class TransactionRequest(BaseModel):
    description: str = Field(..., example="Your A/c XXXXX4321 debited by Rs.425.50 at Zomato Order #ZMTO12345")

class TransactionAnalysis(BaseModel):
    category: str
    Merchant: str
    Transaction: bool

gemini_response_schema = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "Merchant": {"type": "string"},
        "Transaction": {"type": "boolean"},
    },
    "required": ["category", "Merchant", "Transaction"],
}

CATEGORIZE_PROMPT = """
You are an expert AI agent for an expense analyzer.
Analyze a given transaction message and return a JSON object with:
{
  "category": string,
  "Merchant": string,
  "Transaction": boolean
}

Rules:
1. Transaction:
   - true if it's a debit, credit, or purchase message.
   - false if it's an informational or promotional message.

2. category:
   - If Transaction=false → "Miscellaneous"
   - If Transaction=true → one of:
     ["Bills & Utilities", "Education", "Entertainment", "Food & Drinks",
      "Groceries", "Health & Fitness", "Income", "Investments",
      "Miscellaneous", "Shopping", "Travel & Transport"]

3. Merchant:
   - Extract the merchant name (e.g., Zomato, Amazon)
   - If not found or Transaction=false → "NONE"

Return only valid JSON.
"""

# ----------------------------------------------------------------------
# 🧮 AGENT 2: Expense Insights
# ----------------------------------------------------------------------

class MonthData(BaseModel):
    year: int
    month: int
    month_name: str
    total_amount: float
    categories: Dict[str, float]

class InsightResponse(BaseModel):
    monthly_summary: str
    suggestions: List[str]

INSIGHT_PROMPT = """
You are a financial insights AI.
You will receive the user's last 3 months of categorized spending data.

Tasks:
1. Generate a concise summary (3-4 sentences) describing the latest month.
2. Compare trends across the three months.
3. Provide actionable suggestions.

Return strict JSON:
{
  "monthly_summary": "...",
  "suggestions": ["...", "...", "..."]
}
"""

# ----------------------------------------------------------------------
# 🚀 FASTAPI SETUP
# ----------------------------------------------------------------------

app = FastAPI(
    title="AI Expense Analysis System",
    description="Combines categorization and spending insight analysis using Gemini AI",
    version="2.0.0"
)

@app.get("/", include_in_schema=False)
def root():
    return {"status": "AI Expense Analyzer is running."}


# --- Retry logic with fallback keys ---
async def safe_generate(model_func, *args, retries=3):
    for attempt in range(retries):
        try:
            return await model_func(*args)
        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ Rate limit hit. Switching API key (attempt {attempt+1}/{retries})...")
                await asyncio.sleep(1)  # short cooldown
                continue
            else:
                raise
    raise HTTPException(status_code=429, detail="All API keys are rate-limited. Please try again later.")


# --- Agent 1: Transaction Categorizer ---
@app.post("/analyze", response_model=TransactionAnalysis)
async def analyze_transaction(request: TransactionRequest):
    async def run(description):
        model = get_genai_model("gemini-2.0-flash-lite", CATEGORIZE_PROMPT, gemini_response_schema)
        response = await model.generate_content_async([description])
        return TransactionAnalysis.model_validate_json(response.text)

    try:
        return await safe_generate(run, request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")


# --- Agent 2: Expense Insights ---
@app.post("/analyze_insights", response_model=InsightResponse)
async def analyze_insights(months: List[MonthData]):
    async def run(months):
        model = get_genai_model("gemini-2.5-flash", INSIGHT_PROMPT)
        payload = json.dumps({"months": [m.dict() for m in months]}, indent=2)
        response = await model.generate_content_async([payload])
        return InsightResponse.model_validate_json(response.text)

    try:
        return await safe_generate(run, months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

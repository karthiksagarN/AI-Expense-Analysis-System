import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it in your .env file.")

# --- Configure Gemini ---
genai.configure(api_key=API_KEY)

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

categorizer_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=CATEGORIZE_PROMPT,
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": gemini_response_schema,
    }
)

# ----------------------------------------------------------------------
# 🧮 AGENT 2: Expense Insights & Suggestions
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
1. Generate a concise summary (3-4 sentences) describing the latest month (the most recent one).
2. Compare trends across the three months and detect overspending, improvements, and habits.
3. Return personalized, actionable suggestions as a list.

Output format (strict JSON):
{
  "monthly_summary": "...",
  "suggestions": ["...", "...", "..."]
}
"""

insight_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=INSIGHT_PROMPT,
    generation_config={"response_mime_type": "application/json"}
)

# ----------------------------------------------------------------------
# 🚀 FASTAPI SETUP
# ----------------------------------------------------------------------

app = FastAPI(
    title="AI Expense Analysis System",
    description="Combines categorization and spending insight analysis using Gemini AI",
    version="2.0.0"
)

# Root
@app.get("/", include_in_schema=False)
def root():
    return {"status": "AI Expense Analyzer is running."}

# --- Agent 1: Transaction Categorizer ---
@app.post("/analyze", response_model=TransactionAnalysis)
async def analyze_transaction(request: TransactionRequest):
    try:
        response = await categorizer_model.generate_content_async([request.description])
        parsed = TransactionAnalysis.model_validate_json(response.text)
        return parsed
    except Exception as e:
        print(f"❌ Categorizer Error: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

# --- Agent 2: Expense Insights ---
@app.post("/analyze_insights", response_model=InsightResponse)
async def analyze_insights(months: List[MonthData]):
    try:
        payload = json.dumps({"months": [m.dict() for m in months]}, indent=2)
        response = await insight_model.generate_content_async([payload])
        result = InsightResponse.model_validate_json(response.text)
        return result
    except Exception as e:
        print(f"❌ Insights Error: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
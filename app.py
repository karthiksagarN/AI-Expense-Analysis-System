import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it in your .env file.")

# --- Configure Gemini API ---
genai.configure(api_key=API_KEY)

# --- Request Schema ---
class TransactionRequest(BaseModel):
    description: str = Field(..., example="Your A/c XXXXX4321 debited by Rs.425.50 at Zomato Order #ZMTO12345")

# --- Response Schema (Pydantic, for FastAPI output only) ---
class TransactionAnalysis(BaseModel):
    category: str
    Merchant: str
    Transaction: bool

# --- Minimal Gemini-compatible JSON schema (no 'title', 'examples', 'description') ---
gemini_response_schema = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "Merchant": {"type": "string"},
        "Transaction": {"type": "boolean"},
    },
    "required": ["category", "Merchant", "Transaction"],
}

# --- System Prompt ---
SYSTEM_PROMPT = """
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

# --- FastAPI app setup ---
app = FastAPI(
    title="AI Expense Analyzer Agent",
    description="Classify financial transaction messages using Gemini AI",
    version="1.0.0"
)

# --- Gemini model setup ---
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # or gemini-2.5-flash-preview-09-2025
    system_instruction=SYSTEM_PROMPT,
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": gemini_response_schema,  # ✅ custom stripped schema
    }
)

# --- API endpoint ---
@app.post("/analyze", response_model=TransactionAnalysis)
async def analyze_transaction(request: TransactionRequest):
    try:
        response = await model.generate_content_async([request.description])
        parsed = TransactionAnalysis.model_validate_json(response.text)
        return parsed
    except Exception as e:
        print(f"❌ Error during Gemini API call or parsing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing the transaction: {str(e)}"
        )

# --- Root route ---
@app.get("/", include_in_schema=False)
def root():
    return {"status": "AI Expense Analyzer Agent is running."}

# --- Global exception handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

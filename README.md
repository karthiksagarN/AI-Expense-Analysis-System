## 🧾 **AI Expense Analysis System**

![Python](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.101-green) ![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-orange) ![Deploy](https://img.shields.io/badge/Render-Deployed-success)

The **AI Expense Analysis System** is a FastAPI-based microservice powered by **Google Gemini AI** that performs two intelligent functions:

1. 🧠 **Agent 1 – Transaction Categorizer:**
   Classifies a transaction message into a category (e.g., Food, Travel, Shopping) and extracts merchant info.

2. 📊 **Agent 2 – Expense Insights Analyzer:**
   Analyzes the last 3 months of categorized expenses and provides a smart monthly summary + suggestions.

---

## 🚀 **Features**

* 🔍 Categorizes SMS/bank messages using Gemini
* 🧩 Identifies merchants and transaction types (credit/debit/info)
* 📈 Analyzes 3-month expense data for financial insights
* 🗣️ Suggests budgeting improvements and spending trends
* ☁️ Deployable on Render or any FastAPI-compatible host

---

## 🧩 **Project Structure**

```bash
.
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙️ **Setup & Run Locally**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/karthiksagarn/AI-Expense-Analysis-System.git
cd AI-Expense-Analysis-System
```

### 2️⃣ Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```bash
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### 5️⃣ Run the Server

```bash
uvicorn app:app --reload
```

Access the API at:

```
http://127.0.0.1:8000
```

---

## 🧠 **Agent 1 – Transaction Categorization**

### 🔹 Endpoint

`POST /analyze`

### 🔹 Request Example

```json
{
  "description": "Your A/c XXXXX4321 debited by Rs.425.50 at Zomato Order #ZMTO12345"
}
```

### 🔹 Response Example

```json
{
  "category": "Food & Drinks",
  "Merchant": "Zomato",
  "Transaction": true
}
```

---

## 📊 **Agent 2 – Expense Insights Analyzer**

### 🔹 Endpoint

`POST /analyze_insights`

### 🔹 Request Example

Send **last 3 months of expense summaries** as an array:

```json
[
  {
    "year": 2025,
    "month": 9,
    "month_name": "September",
    "total_amount": 15000,
    "categories": {
      "food": 4000,
      "travel": 2000,
      "shopping": 5000,
      "utilities": 3000,
      "entertainment": 1000
    }
  },
  {
    "year": 2025,
    "month": 10,
    "month_name": "October",
    "total_amount": 12000,
    "categories": {
      "food": 3500,
      "travel": 1500,
      "shopping": 4000,
      "utilities": 2000,
      "entertainment": 1000
    }
  },
  {
    "year": 2025,
    "month": 11,
    "month_name": "November",
    "total_amount": 8000,
    "categories": {
      "food": 4000,
      "travel": 2000,
      "shopping": 2000
    }
  }
]
```

### 🔹 Response Example

```json
{
  "monthly_summary": "In November, your spending decreased by 33% compared to October. Food remains the largest category.",
  "suggestions": [
    "Food expenses are consistent and high — consider planning meals.",
    "Good drop in shopping and travel expenses this month.",
    "Maintain the reduced total spending trend."
  ]
}
```

---

## 🌐 **Deployment (Render Example)**

**Start Command**

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Live API Example**

```
https://ai-expense-agent.onrender.com
```

You can test endpoints directly via:

* Swagger UI → `/docs`
* cURL or Postman

---

## 🧰 **Dependencies**

```
fastapi
uvicorn[standard]
google-generativeai
python-dotenv
```

---

## 📜 **License**

This project is licensed under the **MIT License**.

---

Would you like me to include a small **“Usage Workflow Diagram”** (showing how Agent 1 feeds data into Agent 2) in the README for better visual understanding?

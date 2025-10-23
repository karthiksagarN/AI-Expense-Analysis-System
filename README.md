# AI-Expense-Analysis-System

![Python](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.101-green) ![Deploy](https://img.shields.io/badge/deploy-Render-orange)

**AI-Expense-Analysis-System** is a Python FastAPI service that uses Google Gemini API (`gemini-2.5-flash`) to classify bank transaction descriptions. It returns structured JSON responses containing **category**, **merchant**, and **transaction status**.

---

## Project Structure

```bash
.
├── .env
├── .env.example
├── main.py
└── requirements.txt
```

---

## Setup & Run Locally (CLI)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/karthiksagarn/AI-Expense-Analysis-System.git
cd AI-Expense-Analysis-System
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)

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

```bash
cp .env.example .env
nano .env
# Add your Gemini API key in .env:
# GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### 5️⃣ Run the Server

```bash
uvicorn main:app --reload
```

The API is now running at:

```text
http://127.0.0.1:8000
```

### 6️⃣ Test the API via CLI

You can use `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
-H "Content-Type: application/json" \
-d '{"transaction": "Your A/c XXXXX4321 debited by Rs.425.50 at Zomato Order #ZMTO12345"}'
```

**Expected JSON Response:**

```json
{
  "category": "Food & Drinks",
  "merchant": "Zomato",
  "transaction": "True"
}
```

---

## Deployment to Render (CLI-Friendly)

1. **Push to GitHub**

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Web Service on Render**

* Go to Render CLI or Dashboard
* Run CLI command to create a service (if using Render CLI):

```bash
render services create web \
  --name ai-expense-analysis \
  --repo https://github.com/yourusername/AI-Expense-Analysis-System \
  --branch main \
  --build-command "pip install -r requirements.txt" \
  --start-command "uvicorn main:app --host 0.0.0.0 --port $PORT" \
  --env-file .env
```

3. Render will automatically deploy your service. Access the live API at the provided URL.

---

## Example Usage via CLI

```bash
curl -X POST "https://<your-render-url>/analyze" \
-H "Content-Type: application/json" \
-d '{"transaction": "Starbucks Coffee - $5.50"}'
```

**Response:**

```json
{
  "category": "Food & Beverage",
  "merchant": "Starbucks",
  "status": "Debit"
}
```

---

## License

This project is licensed under the MIT License.

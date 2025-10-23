# AI-Expense-Analysis-System

This is a Python FastAPI service that acts as an AI agent for classifying bank transaction descriptions.

It uses the Google Gemini API (gemini-2.5-flash) with JSON mode to analyze a transaction string and return a structured JSON response containing the category, merchant, and transaction status.

Project Structure

.
├── .env
├── .env.example
├── main.py
└── requirements.txt



Setup & Running Locally

Install Dependencies:

pip install -r requirements.txt



Create Environment File:

Copy .env.example to a new file named .env.

cp .env.example .env

Get API Key:

Get your Gemini API key from Google AI Studio.

Paste your key into the .env file:
GEMINI_API_KEY="YOUR_API_KEY_HERE"

Run the Server:

uvicorn main:app --reload



Test the API:

The server will be running at http://127.0.0.1:8000.

Go to http://127.0.0.1:8000/docs to see the interactive (Swagger) API documentation.

You can test the /analyze endpoint directly from that page.

Deployment to Render

This app is ready to deploy on a platform like Render.

Push your code to a GitHub repository.

On the Render dashboard, create a new "Web Service".

Connect your GitHub repository.

Use the following settings:

Runtime: Python 3

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT

Go to the "Environment" tab for your new service.

Add a new "Secret File":

Filename: .env

Contents: GEMINI_API_KEY="YOUR_API_KEY_HERE"

That's it! Render will automatically build and deploy your service. Your backend can then call the URL provided by Render.
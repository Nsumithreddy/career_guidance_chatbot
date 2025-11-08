💬Career Guidance Chatbot:
An AI-powered career mentor chatbot built using FastAPI (backend) and React (frontend). It provides personalized learning advice, roadmaps, and skill-building guidance for students and professionals.

Live Demo

  * Frontend (React on Vercel):`https://career-guidance-chatbot.vercel.app`
  * Backend (FastAPI on Render):`https://career-guidance-backend-iqcx.onrender.com`

Features
  * Real-time AI Responses: Connects to the Google Gemini API to provide intelligent, contextual answers.
  * Full Conversation Memory: All messages (from both the user and the bot) are saved to a session-based database.
  * Modern Full-Stack: A decoupled, scalable backend (FastAPI) and a responsive frontend (React).
  * Clean, Responsive UI: A chat interface built with React that works smoothly on desktop and mobile.

Tech Stack
  * Backend:
      * Python 3.11+
      * FastAPI
      * SQLModel (for database interaction)
      * Uvicorn & Gunicorn (for serving)
  * Frontend:
      * React (with Vite)
      * CSS
  * AI:
      * Google Generative AI (Gemini)
  * Deployment:
      * Backend: Render
      * Frontend: Vercel

How It Works
This application runs as two separate services that communicate via a REST API.

1.  React Frontend (Vercel) sends a `POST` request with the user's message (e.g., `{"content": "Hello"}`) to the backend.
2.  FastAPI Backend (Render) receives the request.
3.  FastAPI saves the user's message to its SQLite database with the `role: "user"`.
4.  FastAPI then sends the *entire* chat history to the Google Gemini API.
5.  Google's AI returns a new message (e.g., `{"content": "Hi! How can I help?"}`).
6.  FastAPI saves this new message to the database with the `role: "bot"`.
7.  FastAPI returns only the bot's message back to the React frontend as the response.
8.  React displays the new message, and the `GET` endpoint provides the full history for display.

How to Run Locally?
This project is a "monorepo" with two parts: `FastAPI` (backend) and `career-chat` (frontend). You must run both in separate terminals.

1. Backend Setup (FastAPI)
  Navigate to the backend folder
  >cd FastAPI
  Create a virtual environment
  >python -m venv venv
  >source venv/bin/activate  # (or venv\Scripts\activate on Windows)

Install requirements
pip install -r requirements.txt

IMPORTANT: Create a .env file
Create a file named ".env" in this /FastAPI folder
and add your Google API key:
GOOGLE_API_KEY="AIza..."

Run the server
uvicorn chatbot:app --reload
Your backend will now be running at `http://127.0.0.1:8000`.

2. Frontend Setup (React)
Open a NEW terminal
cd career-chat

Install dependencies
npm install

Run the app

Your frontend will now be running at `http://127.0.0.1:5173`. Open this URL in your browser.

Deployment
This project is designed for a split deployment.

Backend (Render)

1.  Create a new "Web Service" on Render and connect your GitHub repo.
2.  Set the Root Directory to `FastAPI`.
3.  Build Command: `pip install -r requirements.txt`
4.  Start Command: `gunicorn -k uvicorn.workers.UvicornWorker chatbot:app`
5.  Go to the "Environment" tab and add your secrets:
      * Key: `GOOGLE_API_KEY`
      * Value: `AIza...` (Your secret key)
      * Key: `PYTHON_VERSION`
      * Value: `3.11.9` (or your Python version)

Frontend (Vercel)

1.  Import your GitHub repo into Vercel.
2.  Set the Framework Preset to `Vite`.
3.  Set the Root Directory to `career-chat`.
4.  Go to Settings -> Environment Variables and add your backend's public URL:
      * Key: `VITE_API_BASE`
      * Value: `https://career-guidance-backend-iqcx.onrender.com` (Your Render URL)

Critical: Update CORS
For the deployed frontend to talk to the deployed backend, you must add your Vercel URL to the "Guest List" (CORS) in your FastAPI code.
In `FastAPI/chatbot.py`, update your `origins` list:

origins = [
    "http://localhost:5173",
    "https://career-guidance-chatbot.vercel.app" # <-- ADD THIS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # ...
)

Author
Nagam Sumith Reddy
  * Email: sumithreddynagam23@gmail.com
  * GitHub: [Nsumithreddy](https://www.google.com/search?q=httpsClick%253A//github.com/Nsumithreddy)
  * LinkedIn: [www.linkedin.com/in/sumithreddy-n]
  * Portfolio: [Your Portfolio Website]

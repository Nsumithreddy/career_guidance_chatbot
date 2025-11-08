import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from sqlmodel import SQLModel, create_engine, Session, select, Field
from typing import Optional, List
from contextlib import asynccontextmanager
import google.generativeai as genai  # <- must be this style
from fastapi.middleware.cors import CORSMiddleware 
import time  # this is to measure the time taken for each request
from uuid import uuid4#to generate unique session ids


GEMINI_MODEL = "gemini-2.5-flash"
load_dotenv()
GeminiApi_key = os.getenv("GOOGLE_API_KEY")
if not GeminiApi_key:
    print("Error: Google API key not found, Please check .env file")
else:
    genai.configure(api_key= GeminiApi_key)#we configure the api key to access gemini api for accessing it.


class Message_create(SQLModel):
    content:str

class Chat_Message(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key=True)
    content:str
    role:str#to know who gave the message either the users message or bots generate.
    session_id:str = Field(index=True)

def gen_ai_response(chat_history: List[Chat_Message])->str:
    if not GeminiApi_key:#check api key and then proceed
        return "Error: google api key not found"
    msgs = []
    for message in chat_history:
        if message.role =='bot':
            role = 'model'
        else:
            role = 'user'
        msgs.append({"role":role, "parts":[message.content]})
    if not msgs: 
        return 'return "Say something to start the chat 🙂"'
    #this is the actual steps to make them think and respond 
    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL,system_instruction=(
        "You are an educational and career mentor who guides students and professionals in any field. "
        "You focus only on topics related to learning, skill-building, education, and career growth. "
        "Your role is to provide clear, practical advice—roadmaps, study plans, productivity tips, career strategies, "
        "and real-world learning guidance. "
        "If a user asks something outside education or career growth, politely remind them that you only help with learning and career-related matters, "
        "and redirect the conversation to relevant guidance."),)#this loads the actual ai brain...its like starting the engine 
        chat = model.start_chat(history= msgs[:-1])#gives gemini all the previous conversation except the last one
        msgs[-1]['parts'][0]+="\n\nFormat your answer with short paragraphs, bullet points, and a 7-day starter plan when useful."
        resp = chat.send_message(msgs[-1]["parts"])#send the last user message to gemini to get the response
        return resp.text#returns the gemini replied one and which we save as bot message
    except Exception as e:
        return f"AI error:{e}"


sql_file_name= 'chatbot.db'
sqlite_url= 'sqlite:///chatbot.db'
engine = create_engine(sqlite_url,echo=True)
def create_db_and_table():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    #startup of the requests given to app
    create_db_and_table()
    yield
app = FastAPI(lifespan = lifespan)#calling the lifespan function

from fastapi import Header
@app.post('/chatmessages/',response_model= Chat_Message)
def create_message(message:Message_create, x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        x_session_id = "dev-" + str(uuid4())
    db_Chat = Chat_Message(content=message.content, role="user",session_id=x_session_id)
    with Session(engine) as session:
        session.add(db_Chat)
        session.commit()
        session.refresh(db_Chat)
    
    with Session(engine) as session:
        history = session.exec(
            select(Chat_Message)
            .where(Chat_Message.session_id == x_session_id)
            .order_by(Chat_Message.id.asc())
        ).all()

    bot_text = gen_ai_response(history)
    db_bot = Chat_Message(content=bot_text, role="bot", session_id=x_session_id)
    with Session(engine) as session:
        session.add(db_bot)
        session.commit()
        session.refresh(db_bot)
    return db_bot



@app.get('/chatmessages/',response_model= List[Chat_Message])
def read_messages(x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        x_session_id = "dev-" + str(uuid4())
    with Session(engine) as session:
        messages = session.exec(
            select(Chat_Message)
            .where(Chat_Message.session_id == x_session_id)
            .order_by(Chat_Message.id.asc())
        ).all()
        return messages

@app.delete("/chatmessages/")
def delete_session_history(x_session_id: str = Header(...)):
    with Session(engine) as session:
        items = session.exec(
            select(Chat_Message).where(Chat_Message.session_id == x_session_id)
        ).all()
        for it in items:
            session.delete(it)
        session.commit()
    return {"ok": True}
    
# CORS middleware setup
origins = [
    "http://localhost:5173",
    "https://career-guidance-chat.vercel.app", 
]
app.add_middleware(
    CORSMiddleware,#this is a class we import from fastapi.middleware.cors
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],#this means all methods like get, post, put, delete are allowed
    allow_headers = ["*"],
)

#Logging Middleware 
@app.middleware('http')
async def log_requests(request: Request, call_next):
    start = time.time()  # record the start time
    print(f"➡️  {request.method} {request.url.path}")
    response = await call_next(request)  # this will process the request and get the response
    print(f"⬅️  Done in {time.time()-start:.2f}s")#this will time taken to process the request 
    return response

@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Chatbot:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import psycopg2
from auth import exchange_code_for_tokens, get_user_info
from agent import app_graph
import traceback

load_dotenv()

app = FastAPI()

# this allows frontend to talk with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Database error : {e}")
        raise HTTPException(status_code=500 , detail="Database connection failed")
    
class AuthRequest(BaseModel):
    code: str

@app.get("/")
def read_root():
    return{"status": "Agent is awake", "database": "Connected"}

@app.post("/auth/google")
def google_auth(request: AuthRequest):
    """
    1. Receive Code from Frontend
    2. Exchange for Refresh Token (Google)
    3. Save User + Token to Supabase
    """
    tokens = exchange_code_for_tokens(request.code)

    print("⚠️ GOOGLE ERROR:", tokens)

    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens)
    
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    user_info = get_user_info(access_token)
    email = user_info.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            refresh_token TEXT,
            access_token TEXT
        );
    """)

    # If we got a new refresh token, save it. If not, keep the old one.
    if refresh_token:
        cursor.execute("""
            INSERT INTO users (email, refresh_token, access_token)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) 
            DO UPDATE SET refresh_token = EXCLUDED.refresh_token, access_token = EXCLUDED.access_token;
        """, (email, refresh_token, access_token))
    else:
        # Just update access token
        cursor.execute("""
            UPDATE users SET access_token = %s WHERE email = %s;
        """, (access_token, email))
        
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "User verified", "user": user_info}

class AgentRequest(BaseModel):
    user_id: str
    goal: str

@app.post("/start-agent")
def start_agent(request: AgentRequest):
    return{"message": f"Starting agent for user {request.user_id}", "goal": request.goal}


class RunAgentRequest(BaseModel):
    email:str

@app.post("/run-agent")
async def run_agent(request: RunAgentRequest):
    print(f"🤖 Starting Agent for: {request.email}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT access_token, refresh_token FROM users WHERE email = %s", (request.email,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    access_token, refresh_token = user_data

    config = {
        "configurable": {
            "user_tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }
    }

    try:
        output = await app_graph.ainvoke(
            {"messages": ["Check for unread emails and draft a reply"]}, 
            config=config
        )
        
        # 👇 DEBUGGING: Print exactly what the agent returned
        print("🔍 AGENT OUTPUT:", output)
        
        # 👇 SAFETY CHECK: Use .get() to avoid crashing if key is missing
        messages = output.get("messages", [])
        
        if not messages:
            return {"status": "Agent finished", "agent_response": "No messages returned from agent."}
            
        last_message = messages[-1]
        response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return {"status": "Success", "agent_response": response_text}

    except Exception as e:
        print("CRITICAL ERROR DETAILS:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ =="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
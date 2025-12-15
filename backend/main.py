from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# this allows frontend to talk with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
def read_root():
    return{"status": "Agent is awake", "database": "Connected"}

class AgentRequest(BaseModel):
    user_id: str
    goal: str

@app.post("/start-agent")
def start_agent(request: AgentRequest):
    return{"message": f"Starting agent for user {request.user_id}", "goal": request.goal}

if __name__ =="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
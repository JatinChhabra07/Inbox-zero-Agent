import os
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 1. Update State to hold a LIST of email data
class AgentState(TypedDict):
    messages: List[str]
    email_data: List[dict] # Changed from single snippet to list of dicts
    has_email: bool

# ... (get_gmail_tools function remains the same) ...
def get_gmail_tools(access_token: str, refresh_token: str):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    toolkit = GmailToolkit(api_resource=build_resource_service(credentials=creds))
    return toolkit.get_tools()

# ... (LLM setup remains the same) ...
groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=groq_api_key
)

# 4. Node 1: Check Emails (BATCH MODE)
def check_email_node(state: AgentState, config):
    print("👀 Agent is checking emails...")
    try:
        user_tokens = config.get("configurable", {}).get("user_tokens")
        tools = get_gmail_tools(user_tokens['access_token'], user_tokens['refresh_token'])
        
        search_tool = next((t for t in tools if "search" in t.name), None)
        if not search_tool:
            return {"messages": ["Error: Search tool not found"], "has_email": False}
        
        # Search for UNREAD emails
        result = search_tool.invoke({"query": "is:unread label:inbox"})
        
        if not result:
            return {"messages": ["No unread emails found."], "has_email": False}
        
        # 👇 BATCH LOGIC: Take the top 5 emails
        batch_size = 5
        emails_to_process = result[:batch_size]
        
        email_data_list = []
        for email in emails_to_process:
            email_data_list.append({
                "sender": email.get("sender", "Unknown"),
                "snippet": email.get("snippet", ""),
                "id": email.get("id")
            })
            
        print(f"✅ Found {len(email_data_list)} emails to process.")
        
        return {
            "messages": [f"Found {len(email_data_list)} unread emails."],
            "email_data": email_data_list, # Store list
            "has_email": True
        }
    except Exception as e:
        print(f"Check Email Error: {e}")
        return {"messages": [f"Error checking email: {str(e)}"], "has_email": False}

# 5. Node 2: Draft Replies (BATCH MODE)
def draft_reply_node(state: AgentState, config):
    print("✍️ Agent is drafting replies in batch...")
    try:
        user_tokens = config.get("configurable", {}).get("user_tokens")
        tools = get_gmail_tools(user_tokens['access_token'], user_tokens['refresh_token'])
        draft_tool = next((t for t in tools if "draft" in t.name), None)
        
        if not draft_tool:
             return {"messages": ["Error: Draft tool not found"]}

        results = []
        
        # 👇 LOOP LOGIC: Iterate through the list we found
        for email in state['email_data']:
            sender = email['sender']
            snippet = email['snippet']
            
            prompt = f"Write a polite, professional, and short reply to {sender} regarding this email: '{snippet}'. Sign it as 'My AI Agent'."
            
            # Generate Logic
            response = llm.invoke(prompt)
            draft_body = response.content
            
            # Tool Action
            draft_id = draft_tool.invoke({
                "message": draft_body,
                "to": [sender],
                "subject": "Re: Automated Reply"
            })
            results.append(f"Drafted for {sender} (ID: {draft_id})")
            print(f"   -> Drafted for {sender}")

        return {"messages": [f"Batch Complete! Details: {', '.join(results)}"]}

    except Exception as e:
        print(f"Drafting Error: {e}")
        return {"messages": [f"Failed to draft reply: {str(e)}"]}

# 6. Logic (Same as before)
def should_draft(state: AgentState) -> Literal["draft_reply", END]:
    if state.get("has_email"):
        return "draft_reply"
    return END

# 7. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("check_email", check_email_node)
workflow.add_node("draft_reply", draft_reply_node)

workflow.set_entry_point("check_email")
workflow.add_conditional_edges("check_email", should_draft)
workflow.add_edge("draft_reply", END)

app_graph = workflow.compile()
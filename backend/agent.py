import os
from typing import Literal, TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.get_message import GmailGetMessage
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class AgentState(TypedDict):
    message: List[str]
    email_sender:str
    email_snippet: str
    draft_id: str

def get_gmail_tools(access_token: str, refresh_token:str):
    """
    Reconstructs the Google Credentials using the tokens from Supabase
    """
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

groq_api_key = os.getenv("GROQ_API_KEY", "")
if groq_api_key:
    groq_api_key = groq_api_key.strip()

llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile", 
    api_key=groq_api_key # Pass the clean key
)

#Node 1
def check_email_node(state:AgentState, config):
    print("👀 Agent is checking emails...")

    user_tokens= config.get("configurable", {}).get("user_tokens")
    tools = get_gmail_tools(user_tokens['access_token'], user_tokens['refresh_token'])

    # testing
    tool_names = [t.name for t in tools]
    print(f"Available Tools: {tool_names}")

    # Find search tool
    search_tool = next((t for t in tools if "search" in t.name), None)

    if not search_tool:
        return {"messages": [f"Error: Could not find search tool. Available: {tool_names}"]}

    # Search for UNREAD emails
    result = search_tool.invoke({"query": "is:unread label:inbox"})

    if not result:
        return {"messages": ["No unread emails found."]}
    

    # taking the first email for this demo
    first_email = result[0]

    return {
        "messages": [f"Found email: {first_email['snippet']}"],
        "email_sender": first_email.get("sender", "Unknown"),
        "email_snippet": first_email.get("snippet", ""),
        # Store ID for next step
        "email_id": first_email['id'] 
    }

#  NODE 2: Draft Reply

def draft_reply_node(state: AgentState, config):
    print("✍️ Agent is drafting a reply...")
    
    user_tokens = config.get("configurable", {}).get("user_tokens")
    tools = get_gmail_tools(user_tokens['access_token'], user_tokens['refresh_token'])
    draft_tool = next((t for t in tools if "draft" in t.name), None)

    if not draft_tool:
         return {"messages": ["Error: Could not find draft tool."]}
    
    # Ask LLM to write the email based on the snippet
    email_content = state['email_snippet']
    prompt = f"Write a polite, professional, and short reply to this email: '{email_content}'. Sign it as 'My AI Agent'."
    
    response = llm.invoke(prompt)
    draft_body = response.content

    # Create the draft in Gmail
    try:
            result = draft_tool.invoke({
                "message": draft_body,
                "to": [state['email_sender']],
                "subject": "Re: Automated Reply"
            })
            return {"messages": ["Draft created!", f"Draft Output: {result}"]}
    except Exception as e:
            return {"messages": [f"Failed to draft: {str(e)}"]}
    
def should_draft(state: AgentState) -> Literal["draft_reply", END]:
    """If we found an email, draft a reply. Otherwise, stop."""
    if state.get("has_email"):
        return "draft_reply"
    return END


workflow = StateGraph(AgentState)
workflow.add_node("check_email", check_email_node)
workflow.add_node("draft_reply", draft_reply_node)

workflow.set_entry_point("check_email")

workflow.add_conditional_edges(
    "check_email",
    should_draft
)

workflow.add_edge("draft_reply", END)

app_graph = workflow.compile()
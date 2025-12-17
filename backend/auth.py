import os
import requests
from dotenv import load_dotenv

load_dotenv()

def exchange_code_for_tokens(auth_code: str):
    """
    Swaps the temporary 'auth_code' for a permanent 'refresh_token'.
    """
    token_url = "https://oauth2.googleapis.com/token"
    

    payload = {
        "code": auth_code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "postmessage",  
        "grant_type": "authorization_code",
    }
    

    response = requests.post(token_url, data=payload)

    return response.json()

def get_user_info(access_token: str):
    """
    Uses the access token to ask Google 'Who is this person?'
    """
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(user_info_url, headers=headers)

    return response.json()
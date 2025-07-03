"""
Stub endpoints and integration points for Resend (outgoing reminders) and Gmail OAuth2 (connect/disconnect, fetch recent event emails).
Also includes credential/environment variable setup instructions and background scheduler (APScheduler) board.

- Resend is used to send outgoing email reminders.
- Gmail OAuth2 flow allows users to connect their Gmail for reading calendar-related emails.

ENVIRONMENT VARIABLES (add these to your .env and keep secure!):

# Resend setup (https://resend.com/)
RESEND_API_KEY="your_resend_api_key"

# Google OAuth2 (Gmail API, https://console.cloud.google.com/apis/credentials)
GOOGLE_CLIENT_ID="your_client_id"
GOOGLE_CLIENT_SECRET="your_client_secret"
GOOGLE_OAUTH_REDIRECT_URI="your_oauth_callback_url"
GOOGLE_AUTH_SCOPE="https://www.googleapis.com/auth/gmail.readonly"
# Optionally also GOOGLE_PROJECT_ID (may be needed for some APIs)

# Securely store all values above! Never hardcode in code.

Setup instructions are at the end of this file.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from dotenv import load_dotenv

from .auth import clerk_jwt_required

router = APIRouter(prefix="/email", tags=["email"])

load_dotenv()

# Public endpoints to guide user to connect Gmail and to send reminders using Resend

# Resend API stub
def send_reminder_via_resend(to_email: str, subject: str, content: str) -> bool:
    """
    (Stub) Send an email reminder using the Resend API.
    You must sign up at https://resend.com, create an API key, and add RESEND_API_KEY to your .env.
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        # Not set up yet
        raise RuntimeError("RESEND_API_KEY not set. See /email/setup-help for instructions.")
    # TODO: Implement API call to Resend to actually send email (use `requests` or `httpx`)
    return True

# PUBLIC_INTERFACE
@router.post("/remind", summary="Send email reminder via Resend (stub)")
async def trigger_reminder_stub(
    request: Request,
    user_claims=Depends(clerk_jwt_required)
):
    """
    Send a test reminder using Resend (stub only).
    POST body: {'email': str, 'subject': str, 'content': str}
    """
    body = await request.json()
    to_email = body.get('email')
    subject = body.get('subject', 'Reminder')
    content = body.get('content', 'This is a reminder.')
    if not to_email:
        raise HTTPException(status_code=400, detail="Email field required.")
    try:
        send_reminder_via_resend(to_email, subject, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"result": "sent (stub)", "email": to_email}


# --- Gmail OAuth2 flow (stub) ---

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
GOOGLE_AUTH_SCOPE = os.getenv("GOOGLE_AUTH_SCOPE", "https://www.googleapis.com/auth/gmail.readonly")

# For production: implement token storage
_oauth_tokens = {}

def get_google_oauth_url():
    """Compose Google's OAuth2 URL for account connection."""
    import urllib.parse
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID or "your_client_id",
        "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI or "your_redirect_uri",
        "response_type": "code",
        "scope": GOOGLE_AUTH_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{base}?{urllib.parse.urlencode(params)}"

# PUBLIC_INTERFACE
@router.get("/gmail/connect", summary="Start Gmail OAuth2 connect flow")
def gmail_connect(user_claims=Depends(clerk_jwt_required)):
    """Redirect user to Google OAuth2 authorization to connect Gmail."""
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_OAUTH_REDIRECT_URI):
        raise HTTPException(status_code=500, detail="Google credentials not set. See /email/setup-help for instructions.")
    url = get_google_oauth_url()
    return {"authorization_url": url}

# PUBLIC_INTERFACE
@router.get("/gmail/oauth-callback", summary="Handle Gmail OAuth2 callback (stub)")
def gmail_oauth_callback(code: Optional[str] = None, error: Optional[str] = None):
    """
    Handles Google OAuth2 redirect.
    On production: Exchange 'code' for access_token, store with user, etc.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Gmail OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code'")
    # TODO: Exchange code for access/refresh token, store/associate with user
    token = "dummy_access_token"
    # _oauth_tokens[user_id] = token  # Example
    return {"token": token, "message": "OAuth2 callback handled (stub)"}

# PUBLIC_INTERFACE
@router.get("/gmail/disconnect", summary="Disconnect Gmail for current user (stub)")
def gmail_disconnect(user_claims=Depends(clerk_jwt_required)):
    """
    Remove stored Gmail tokens for the current user (stub).
    """
    # TODO: Remove user token from _oauth_tokens, DB, etc.
    return {"result": "Gmail disconnected (stub)"}

# PUBLIC_INTERFACE
@router.get("/gmail/recent", summary="Fetch user's recent event-related emails from Gmail (stub)")
def gmail_recent_emails(user_claims=Depends(clerk_jwt_required)):
    """Fetch recent event-related emails from user's Gmail account (stub only)."""
    # TODO: Use Google API with stored token per user, filter for calendar/events emails
    return {
        "emails": [
            {"subject": "[Fake] Event update!", "snippet": "Here's your event update.", "from": "calendar@example.com"}
        ],
        "note": "Gmail API integration stub"
    }


# --- SETUP/HELP ENDPOINT ---

# PUBLIC_INTERFACE
@router.get("/setup-help", summary="Credential/environment variable setup instructions")
def email_credential_help():
    """
    Returns instructions on how to get the required API keys/credentials and which environment variables are needed.
    """
    return {
        "resend": {
            "register": "https://resend.com/",
            "instructions": "Sign up for a Resend account. Go to API Keys, create a key. Add RESEND_API_KEY to your .env file."
        },
        "gmail": {
            "console_url": "https://console.cloud.google.com/apis/credentials",
            "instructions": [
                "1. Go to Google Cloud Console. Create an OAuth2 Client ID for a web application.",
                "2. Add your frontend and /gmail/oauth-callback endpoint as authorized redirect URIs.",
                "3. Add the CLIENT_ID and CLIENT_SECRET to your .env as GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_OAUTH_REDIRECT_URI.",
                f"4. Use scope: {GOOGLE_AUTH_SCOPE}"
            ]
        },
        "required_env_vars": [
            "RESEND_API_KEY",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "GOOGLE_OAUTH_REDIRECT_URI"
        ],
        "secure_storage": "Store all credentials in .env. Do NOT commit this file. Use environment settings for production security."
    }

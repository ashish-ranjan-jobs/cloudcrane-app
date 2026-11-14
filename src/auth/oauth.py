#!/usr/bin/env python3
"""
CloudCrane OAuth 2.0 PKCE Helper & MCP Client
"""

import os
import sys
import json
import base64
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUTH_STATE_FILE = BASE_DIR / ".auth_state.json"
TOKEN_FILE = BASE_DIR / ".token.json"

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge

def register_client(redirect_uri="http://localhost:8080/callback"):
    url = "https://cloudcrane.ai/api/oauth/register"
    payload = {
        "client_name": "CloudCrane Antigravity Assistant",
        "redirect_uris": [redirect_uri],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_authorization_url(redirect_uri="http://localhost:8080/callback"):
    client_info = register_client(redirect_uri)
    client_id = client_info["client_id"]
    code_verifier, code_challenge = generate_pkce()
    state = base64.urlsafe_b64encode(os.urandom(16)).decode("utf-8").rstrip("=")
    
    # Save auth state for token exchange
    state_data = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "state": state
    }
    with open(AUTH_STATE_FILE, "w") as f:
        json.dump(state_data, f, indent=2)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "apps:read apps:write",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state
    }
    auth_url = f"https://cloudcrane.ai/api/oauth/authorize?{urllib.parse.urlencode(params)}"
    return auth_url, state_data

def exchange_code_for_token(code_or_url):
    if not AUTH_STATE_FILE.exists():
        raise RuntimeError("No auth state found. Please run init_auth first.")

    with open(AUTH_STATE_FILE, "r") as f:
        state_data = json.load(f)

    # Extract code if full URL was provided
    code = code_or_url.strip()
    if "code=" in code:
        parsed = urllib.parse.urlparse(code)
        qs = urllib.parse.parse_qs(parsed.query)
        if "code" in qs:
            code = qs["code"][0]

    token_url = "https://cloudcrane.ai/api/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": state_data["client_id"],
        "code": code,
        "redirect_uri": state_data["redirect_uri"],
        "code_verifier": state_data["code_verifier"]
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        token_url,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT
        }
    )
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode("utf-8"))

    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return tokens

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "exchange":
        if len(sys.argv) < 3:
            print("Usage: python3 oauth.py exchange <code_or_callback_url>")
            sys.exit(1)
        res = exchange_code_for_token(sys.argv[2])
        print("Success! Tokens received:")
        print(json.dumps(res, indent=2))
    else:
        url, state = get_authorization_url()
        print("Authorization URL:")
        print(url)

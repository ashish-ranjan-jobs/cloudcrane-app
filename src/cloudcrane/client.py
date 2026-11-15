#!/usr/bin/env python3
"""
CloudCrane MCP Client over Streamable HTTP with Bearer Token
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUTH_STATE_FILE = BASE_DIR / ".auth_state.json"
TOKEN_FILE = BASE_DIR / ".token.json"

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MCP_URL = "https://cloudcrane.ai/api/apps/mcp"

class CloudCraneMCPClient:
    def __init__(self, token=None):
        self.token = token or self._load_token()
        self.request_id = 0

    def _load_token(self):
        if not TOKEN_FILE.exists():
            raise FileNotFoundError("No token found. Please complete OAuth flow first.")
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        return data.get("access_token")

    def refresh_token(self):
        if not AUTH_STATE_FILE.exists() or not TOKEN_FILE.exists():
            return False
        with open(AUTH_STATE_FILE, "r") as f:
            auth_state = json.load(f)
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)

        payload = {
            "grant_type": "refresh_token",
            "client_id": auth_state["client_id"],
            "refresh_token": token_data["refresh_token"]
        }
        req = urllib.request.Request(
            "https://cloudcrane.ai/api/oauth/token",
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                new_tokens = json.loads(resp.read().decode("utf-8"))
                token_data.update(new_tokens)
                with open(TOKEN_FILE, "w") as f:
                    json.dump(token_data, f, indent=2)
                self.token = new_tokens.get("access_token")
                return True
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def rpc_call(self, method, params=None):
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {self.token}"
        }
        req = urllib.request.Request(MCP_URL, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                if self.refresh_token():
                    headers["Authorization"] = f"Bearer {self.token}"
                    req = urllib.request.Request(MCP_URL, data=data, headers=headers)
                    with urllib.request.urlopen(req) as resp:
                        raw = resp.read().decode("utf-8")
                        return json.loads(raw)
            raise

    def initialize(self):
        return self.rpc_call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "CloudCrane Antigravity Python Client",
                "version": "1.0.0"
            }
        })

    def list_tools(self):
        return self.rpc_call("tools/list")

    def call_tool(self, name, arguments=None):
        return self.rpc_call("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })

    def list_apps(self):
        return self.call_tool("list_apps")

    def get_app(self, slug):
        return self.call_tool("get_app", {"slug": slug})

    def publish_app(self, name, purpose, code, blueprint=None):
        args = {"name": name, "purpose": purpose, "code": code}
        if blueprint:
            args["blueprint"] = blueprint
        return self.call_tool("publish_app", args)

    def update_app(self, app, html=None, blueprint=None, note=None, look=True):
        args = {"app": app}
        if html:
            args["html"] = html
        if blueprint:
            args["blueprint"] = blueprint
        if note:
            args["note"] = note
        if look is not None:
            args["look"] = look
        return self.call_tool("update_app", args)

    def look_at_app(self, app, version=None):
        args = {"app": app}
        if version:
            args["version"] = version
        return self.call_tool("look_at_app", args)

    def try_app(self, app=None, html=None, blueprint=None):
        args = {}
        if app:
            args["app"] = app
        if html:
            args["html"] = html
        if blueprint:
            args["blueprint"] = blueprint
        return self.call_tool("try_app", args)

    def rollback_app(self, app, version):
        return self.call_tool("rollback_app", {"app": app, "version": version})

    def get_spec_guide(self):
        return self.call_tool("get_spec_guide")

    def get_design_guide(self):
        return self.call_tool("get_design_guide")

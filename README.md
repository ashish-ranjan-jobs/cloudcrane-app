# CloudCrane Job Application Tracker

A mobile-first phone app built for the CloudCrane hiring challenge.

**What it does:** Track job applications — add positions, update statuses, 
set reminders, and see your pipeline at a glance. Built iteratively over 3+ versions.

## Project Structure
```
cloudcrane-app/
├── venv/                    # Python virtualenv (not committed)
├── requirements.txt         # Dependencies
├── src/
│   ├── auth/
│   │   ├── oauth_server.py  # Local OAuth callback listener
│   │   └── token_store.py   # Persist & refresh tokens
│   ├── cloudcrane/
│   │   ├── client.py        # CloudCrane MCP API client
│   │   └── builder.py       # App HTML/JS builder
│   └── app/
│       ├── spec.py          # App spec/blueprint definitions
│       └── versions.py      # Version manager
├── apps/
│   ├── v1/                  # Version 1: basic tracker
│   ├── v2/                  # Version 2: + status history
│   └── v3/                  # Version 3: + notes + tags
├── tests/
├── main.py                  # CLI entry point
└── .env.example
```

## Setup
```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py auth      # OAuth login to CloudCrane
python main.py build v1  # Publish Version 1
python main.py build v2  # Publish Version 2
python main.py build v3  # Publish Version 3
```

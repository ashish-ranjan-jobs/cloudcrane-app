import json
from src.cloudcrane.client import CloudCraneMCPClient

client = CloudCraneMCPClient()

blueprint = {
    "v": 1,
    "purpose": "A personal job application tracker to track companies, interview stages, and offers directly on your phone.",
    "screens": [
        {
            "id": "pipeline",
            "says": "Pipeline overview with stage counts, search filter, and list of job applications."
        },
        {
            "id": "add-app",
            "says": "Bottom sheet to log a new job application with company name, role, stage, and date."
        }
    ],
    "data": {
        "version": 1,
        "keeps": [
            {
                "key": "applied_data",
                "what": "Job applications saved on this phone with company, role, stage, date, and salary expectations.",
                "shape": {
                    "applications": "list",
                    "version": "number"
                },
                "personal": False
            }
        ]
    },
    "journeys": [
        {
            "id": "J-1",
            "title": "Log a job application",
            "steps": [
                {"id": "J-1.1", "text": "Tap the Add Application button"},
                {"id": "J-1.2", "text": "Enter company name and role"},
                {"id": "J-1.3", "text": "Tap Save Application and see it appear in the pipeline list"}
            ]
        },
        {
            "id": "J-2",
            "title": "Change application status",
            "steps": [
                {"id": "J-2.1", "text": "Tap an application to view details"},
                {"id": "J-2.2", "text": "Select a new stage such as Interview or Offer"},
                {"id": "J-2.3", "text": "See the pipeline counts update immediately"}
            ]
        }
    ],
    "promises": [
        {
            "id": "P-1",
            "text": "Job applications saved on this phone persist across app restarts and work completely offline.",
            "kind": "data"
        }
    ],
    "icon": "briefcase",
    "category": "productivity",
    "tags": ["jobs", "careers", "tracker", "interviews", "pipeline"]
}

html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Applied</title>
  <style>
    :root {
      --bg: #0f1419;
      --card: #19222c;
      --fg: #f1f5f9;
      --muted: #94a3b8;
      --primary: #38bdf8;
      --primary-fg: #0f172a;
      --accent: #f59e0b;
      --border: #2e3e50;
      font-family: system-ui, -apple-system, sans-serif;
      color-scheme: dark;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--fg);
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      padding-top: env(safe-area-inset-top);
      padding-bottom: env(safe-area-inset-bottom);
      -webkit-font-smoothing: antialiased;
    }
    header {
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
    }
    h1 { font-size: 1.35rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    main { flex: 1; padding: 16px; overflow-y: auto; overscroll-behavior: contain; }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 20px;
    }
    .stat-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 6px;
      text-align: center;
    }
    .stat-num { font-size: 1.25rem; font-weight: 800; color: var(--primary); }
    .stat-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; margin-top: 2px; }
    .btn {
      min-height: 44px;
      padding: 12px 18px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      touch-action: manipulation;
    }
    .btn-primary { background: var(--primary); color: var(--primary-fg); }
    .empty-state { text-align: center; padding: 48px 16px; color: var(--muted); }
  </style>
</head>
<body>
  <header>
    <h1>Applied</h1>
    <button id="addBtn" class="btn btn-primary" style="min-height: 38px; padding: 6px 14px; font-size: 0.9rem;">+ Add</button>
  </header>
  <main>
    <div class="stats">
      <div class="stat-card"><div class="stat-num" id="sApplied">0</div><div class="stat-label">Applied</div></div>
      <div class="stat-card"><div class="stat-num" id="sInterview">0</div><div class="stat-label">Interview</div></div>
      <div class="stat-card"><div class="stat-num" id="sOffer">0</div><div class="stat-label">Offer</div></div>
      <div class="stat-card"><div class="stat-num" id="sRejected">0</div><div class="stat-label">Rejected</div></div>
    </div>
    <div id="appList">
      <div class="empty-state">
        <p>No job applications logged yet.</p>
        <p style="font-size: 0.85rem; margin-top: 6px;">Tap "+ Add" to track your first application.</p>
      </div>
    </div>
  </main>
  <script>
    (function() {
      const KEY = 'applied_data';
      function getStore() {
        try {
          const raw = localStorage.getItem(KEY);
          return raw ? JSON.parse(raw) : { version: 1, applications: [] };
        } catch(e) {
          return { version: 1, applications: [] };
        }
      }
      function saveStore(data) {
        localStorage.setItem(KEY, JSON.stringify(data));
      }
      window.appState = getStore;
    })();
  </script>
</body>
</html>"""

res = client.call_tool("check_publish", {
    "name": "Applied",
    "blueprint": blueprint,
    "html": html
})
print("Check publish result:")
print(json.dumps(res, indent=2))

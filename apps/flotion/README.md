# Flotion

A deliberately small **Notion clone** — the demo application that the 5-agent
cmux team builds and operates. Vue 3 + TypeScript on the front, FastAPI +
SQLite on the back.

```
apps/flotion/
├── backend/            # FastAPI + stdlib sqlite3 (no ORM)
│   ├── main.py         #   pages + blocks CRUD, CORS, seed, /api/health
│   ├── pyproject.toml  #   uv-managed deps (fastapi, uvicorn)
│   └── flotion.db      #   created on first run (gitignored)
├── frontend/           # Vite + Vue 3 + TS
│   ├── src/
│   │   ├── App.vue           # shell: sidebar + page view
│   │   ├── api.ts            # typed REST client
│   │   └── components/       # Sidebar, PageView, BlockItem
│   └── vite.config.ts        # dev proxy /api -> :8000
└── justfile            # install / be / fe / dev / build / reset-db
```

## Run it

```bash
cd apps/flotion
just install      # uv sync (backend) + npm install (frontend)
just dev          # backend :8000 + frontend :5173 together (Ctrl-C stops both)
# …or, the way the agent team runs it — one per pane:
just be           # FastAPI  on http://localhost:8000
just fe           # Vite app on http://localhost:5173
```

Open **http://localhost:5173**. You get a sidebar of pages and an editable
page made of text blocks. Everything persists to `backend/flotion.db`.

## Data model

```
pages  (id, title, parent_id, position, created_at, updated_at)
blocks (id, page_id, type, content, position, created_at, updated_at)
```

`parent_id` is already in the schema so nested pages are a small extension —
exactly the kind of feature the agent team picks up.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | liveness probe |
| GET | `/api/pages` | list pages |
| POST | `/api/pages` | create page `{title}` |
| GET | `/api/pages/{id}` | page + its blocks |
| PATCH | `/api/pages/{id}` | update `{title, parent_id, position}` |
| DELETE | `/api/pages/{id}` | delete page (cascades to blocks) |
| POST | `/api/pages/{id}/blocks` | add block `{type, content, position}` |
| PATCH | `/api/blocks/{id}` | update `{type, content, position}` |
| DELETE | `/api/blocks/{id}` | delete block |

## Where the agents fit

This is the *working baseline*. The team in [`.claude/agents/`](../../.claude/agents)
extends it live: the **plan** agent scopes a feature, **build-be** and
**build-fe** implement it, **test** verifies, and **lead** coordinates the four
through cmux. An orchestrator (`just devcc` / `just devpi`) boots the team into
its own cmux window via the `/spawn-fs-team` command (see
[`.claude/commands/spawn-fs-team.md`](../../.claude/commands/spawn-fs-team.md)).

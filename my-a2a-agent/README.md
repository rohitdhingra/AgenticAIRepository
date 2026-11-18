# My A2A Agent

A minimal Python A2A project with a FastAPI agent server and an HTTP JSON-RPC client.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

Start the server:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal, send a message:

```bash
source .venv/bin/activate
python client.py "Hello, A2A!"
```

The agent card is available at `http://127.0.0.1:8000/.well-known/agent-card.json`.

## Test

```bash
pytest
```

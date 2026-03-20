# MIS – Memory Identity Stratified (Ultimate Level)

MIS is a desktop cognitive-twin AI foundation with persistent memory, structured identity, and adaptive reasoning.

## Core Capabilities
- Persistent long-term memory with SQLite
- Short-term conversational memory window
- Dynamic identity/profile engine with onboarding traits
- Prompt engine with context selection and size limits
- AI connector abstraction with safe fallback behavior
- Tkinter desktop UI with chat, profile, and memory views

## Quick Start
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build EXE (Windows)
```bash
pyinstaller --noconfirm --onefile --windowed --name MIS main.py
```

## Data and Persistence
- Database: `data/mis.db`
- Logs: `data/mis.log`
- Settings: `config/settings.json`

## Notes
- Replace `MockAIConnector` with a provider-specific connector to use real APIs.
- SQLite WAL mode is enabled for safer concurrent reads/writes.

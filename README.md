# Dev-Notebook-LM

A simple personal study notebook web app that summarizes pasted notes and generates study flashcards using the Hugging Face chat-completions API. Built with Flask and storing notes locally in a SQLite database.

**Features**
- **Summarize**: Paste or type notes and get a concise AI-generated summary.
- **Flashcards**: Auto-generate Q/A flashcards from notes for quick study.
- **History**: View previously saved notes, summaries, and generated flashcards.
- **Study mode**: View the most recently generated flashcards in a simple study view.

**Files**
- `app.py` - Flask application and core logic (API calls, DB init, routes).
- `requirements.txt` - Python dependencies.
- `templates/` - HTML templates: `index.html`, `login.html`, `study.html`, `history.html`.

**Requirements**
- Python 3.8+ (or compatible)
- See `requirements.txt` for the Python packages used (Flask, requests).

**Environment variables**
- `HF_API_KEY` - (required) Hugging Face API key used by the app for AI summarization and flashcard generation.

**Quick start**
1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Export your Hugging Face API key (example for Linux/macOS):

```bash
export HF_API_KEY="your_hf_api_key_here"
```

4. Run the app:

```bash
python app.py
```

5. Open http://127.0.0.1:5000 in your browser.

Optional: use a `.env` file


1. Edit `.env` and replace placeholders, then export variables in your shell session:

**Usage**
- Visit the app and log in using any username (no password). The session saves a simple `user` identifier.
- Paste or type notes on the main page and submit to generate a summary and flashcards. Saved notes are stored in `notes.db` (created automatically on first run).
- Use the **Study** page to view parsed flashcards and **History** to browse previous entries.

**Development notes & security**
- The app currently sets `app.secret_key` inside `app.py`. For production, move the secret key to an environment variable and never commit it to source control.
- The Hugging Face API may incur usage limits or costs; ensure you monitor usage of `HF_API_KEY`.

**Troubleshooting**
- If the AI model reports it's loading or returns errors, the app includes retries for flashcard generation, but you may need to wait or try a different model/API settings.
------------

# Dev-Notebook-LM

A simple personal study notebook web app that summarizes pasted notes and generates study. Built with Flask.

**Features**
- **Summarize**: Paste or type notes and get a concise AI-generated summary.
- **Flashcards**: Auto-generate Q/A flashcards from notes for quick study.
- **History**: View previously saved notes, summaries, and generated flashcards.
- **Study mode**: View the most recently generated flashcards in a simple study view.


**Environment variables**
- `HF_API_KEY` - (required)

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

3. Export your Hugging Face API key:

```bash
export HF_API_KEY="your_hf_api_key_here"
```

4. Run the app:

```bash
python app.py
```

5. Open http://127.0.0.1:5000 in your browser.

## Author

Developed by Devin

---

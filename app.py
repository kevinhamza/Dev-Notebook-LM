import time
from flask import Flask , render_template , request
from flask import session, redirect, url_for
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "devbooklm-secret-key"

init_db() # temp add for vercel

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    result=""
    flashcard=""
    if request.method == "POST":
        notes = request.form["notes"]
        result = get_ai_summary(notes)
        flashcard = generate_flashcard(notes)
        conn = sqlite3.connect("/tmp/notes.db") # tmp add for vercel
        cursor = conn.cursor()
        username = session["user"]
        cursor.execute(
            "INSERT INTO notes (username, content, summary, flashcards) VALUES (?, ?, ?, ?)",
            (username, notes, result, flashcard)
            )
        conn.commit()
        conn.close()
    return render_template("index.html", result=result, flashcard=flashcard)
def get_ai_summary(text):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization" : f"Bearer {os.getenv('HF_API_KEY')}",
        "Content-Type" : "application/json"
    }
    payload = {
        "model" : "deepseek-ai/DeepSeek-V3.2:novita",
        "messages" : [
            {"role" : "system", "content" : "You are an expert summarizer."},
            {"role" : "user", "content" : f"Summarize this text in as few words as possible while retaining key information:\n{text}"}
        ]
    }
    response = requests.post(API_URL, headers = headers, json = payload, timeout=30)
    try:
        data = response.json()
    except Exception:
        return f"Error parsing response: {response.text}"
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    elif isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    elif isinstance(data, dict) and "error" in data:
        return f"API Error: {data['error']}"
    else:
        return str(data)
def generate_flashcard(text):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization" : f"Bearer {os.getenv('HF_API_KEY')}",
            "Content-Type" : "application/json"
            }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3.2:fastest",
        "messages": [
            {"role": "system", "content": "You are an expert teacher."},
            {"role": "user", "content": f"Generate study flashcards from this text and also adjust the numbers of Questions and answers according to the text length and each question and answer should be concise and clear and on each line:\n{text}\nFormat as:\nQ1: <question>\nA1: <answer>\nQ2: <question>\nA2: <answer>\nQ3: <question>\nA3: <answer>\nQn: <question>\nAn: <answer>"}
        ]
    }
    max_tries = 5
    for attempt in range(max_tries):
        try:
            response = requests.post(API_URL, headers = headers, json=payload, timeout=30)
            try:
                data = response.json()
            except Exception:
                data = {"error" : f"Non-JSON response: {response.text[:200]}"}
            if "error" in data and "loading" in data["error"].lower():
                print(f"Attempt {attempt+1} : Model is loading, retrying in 10 seconds...")
                time.sleep(10)
                continue
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            
            return str(data)
        except Exception as e:
            print(f"Attempt {attempt+1} : Error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    return "Failed to generate flashcards after multiple attempts. Please try again later."

def init_db():
    conn = sqlite3.connect("/tmp/notes.db") # for vercel
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT,
        summary TEXT,
        flashcards TEXT)
    """)
    conn.commit()
    conn.close()
def parse_flashcards(text):
    lines = text.split("\n")
    cards = []
    question = ""
    answer = ""
    for line in lines:
        line = line.strip()
        if line.startswith("Q"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                question = parts[1].strip()
        elif line.startswith("A"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                answer = parts[1].strip()
                cards.append((question, answer))
    return cards
    
@app.route("/study")
def study():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("/tmp/notes.db")
    cursor = conn.cursor()
    username = session["user"]
    cursor.execute("SELECT flashcards FROM notes WHERE username = ? ORDER BY id DESC LIMIT 1", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        cards = parse_flashcards(result[0])
    else:
        cards = []
    return render_template("study.html", cards = cards)

@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("/tmp/notes.db")
    cursor = conn.cursor()
    username = session["user"]
    cursor.execute("SELECT content, summary, flashcards FROM notes WHERE username = ? ORDER BY id DESC", (username,))
    data = cursor.fetchall()
    conn.close()
    return render_template("history.html", data=data)
@app.route("/login", methods=["GET", "POST"])
def login(): 
    if request.method == "POST":
        username = request.form["username"].strip()
        if username:
            session["user"] = username
            return redirect(url_for("home"))
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    # init_db() for vercel comment
    app.run(debug=True)

handler = app

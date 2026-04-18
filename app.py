import time
from flask import Flask , render_template , request
from flask import session, redirect, url_for
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hakdjsjsiieeaajjdjdjxncnxmsms"

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    result=""
    flashcard=""
    if request.method == "POST":
        notes = request.form.get("notes", "").strip()
        if not notes:
            return render_template("index.html", result="Please enter some text", flashcard="")
        result = get_summary(notes)
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
def get_summary(text):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization" : f"Bearer {os.getenv('HF_API_KEY')}",
        "Content-Type" : "application/json"
    }
    payload = {
        "model" : "meta-llama/Meta-Llama-3-8B-Instruct",
        "messages" : [
            {"role" : "system", "content" : "You are an expert summarizer"},
            {"role" : "user", "content" : f"Summarize this text in as few words as possible while keep all concepts:\n{text}"}
        ]
    }
    res = requests.post(API_URL, headers = headers, json = payload, timeout=30)
    try:
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"Error parsing response: {res.text}"
def generate_flashcard(text):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization" : f"Bearer {os.getenv('HF_API_KEY')}",
            "Content-Type" : "application/json"
            }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
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
                return data["choices"][0]["message"]["content"]
            except Exception:
                data = {"error" : f"Non-JSON response: {response.text[:200]}"}
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

init_db()

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
    app.run()



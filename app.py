"""
app.py
------
Flask web app that wraps model_router.call_model() behind a small
JSON API, plus a simple session-based "sign in with a name" screen
and a chat page.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

from model_router import call_model

load_dotenv()

app = Flask(__name__)

_secret_key = os.getenv("FLASK_SECRET_KEY")
if not _secret_key:
    if os.getenv("FLASK_ENV") == "production":
        raise RuntimeError(
            "FLASK_SECRET_KEY is not set. Set it in your environment before "
            "running in production (see .env.example)."
        )
    _secret_key = "dev-secret-change-me"
app.secret_key = _secret_key

# In-memory conversation store, keyed by session id.
# Fine for a single-user demo / resume project; swap for a real DB (or
# Redis) if you ever need multiple concurrent users at scale.
conversations: dict[str, list[dict]] = {}


def get_history() -> list[dict]:
    sid = session.get("user")
    if sid not in conversations:
        conversations[sid] = []
    return conversations[sid]


@app.route("/", methods=["GET"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["user"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            return render_template("login.html", error="Please enter a name to continue.")
        session["user"] = username
        conversations.setdefault(username, [])
        return redirect(url_for("home"))
    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/api/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"error": "Not signed in"}), 401

    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    history = get_history()
    history.append({"role": "user", "content": user_input})

    reply, model_used = call_model(user_input, history)

    history.append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply, "model": model_used})


@app.route("/api/clear", methods=["POST"])
def clear_chat():
    if "user" in session:
        conversations[session["user"]] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV", "development") != "production"
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

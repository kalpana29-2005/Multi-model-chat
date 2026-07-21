# 🤖 Multi Model Chat – AI Chat System

Multi Model Chat is a powerful AI chatbot that intelligently routes user queries to different AI models based on the task type. It is designed to be fast, modular, and easily extendable for real-world applications.

---

## 🚀 Features

 **Multi-Model Routing** – Automatically selects the best model for each query
 **ChatGPT-like UI** – Clean and responsive Flask-based interface
 **Fast Responses** – Optimized routing logic
 **Smart Classification** – Detects query type (coding, general, reasoning, etc.)
 **Plug & Play Models** – Easily integrate APIs or local models
 **Web Interface** – Runs in browser

---

## 🏗️ Project Structure

```
Multi-Model-Chat/
│── app.py              # Main Flask app
│── model_router.py     # Routes queries
│── templates/
│   └── index.html
|
│── static/
│   └── style.css
│── requirements.txt
│── README.md

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/kalpana29-2005/multi-model-chat.git
cd multi-model-chat
```

### 2️⃣ Create virtual environment (optional)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up your environment variables

```bash
cp .env.example .env
```

Then edit `.env` and fill in your real `GITHUB_API_KEY`, `GROQ_API_KEY`, and a
random `FLASK_SECRET_KEY`. **Never commit your real `.env` file** — it's
already excluded via `.gitignore`.

---

## ▶️ Run the App (local development)

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## ☁️ Deploying

The app ships with a `Procfile` and `gunicorn`, so it works out of the box on
Render, Railway, or Heroku-style platforms:

1. Push this repo to GitHub.
2. Create a new web service on your platform of choice, pointing at the repo.
3. Set the environment variables from `.env.example` (`GITHUB_API_KEY`,
   `GROQ_API_KEY`, `FLASK_SECRET_KEY`, `FLASK_ENV=production`) in the
   platform's dashboard — do not put real keys in any file you commit.
4. The platform will run the `Procfile`'s start command:
   `gunicorn app:app --bind 0.0.0.0:$PORT`.

> ⚠️ **Security note:** conversation history is stored in memory
> (`conversations` dict in `app.py`), so it resets on every restart/deploy and
> won't scale across multiple server instances. Fine for a demo; swap in a
> real database (SQLite/Postgres) if you need persistence.

---

## 🧠 How It Works

1. User enters a query
2. `model_router.py` analyzes it
3. Routes to:

   * Coding → Code Model
   * General → GPT Model
   * Logic → Specialized Model
4. Response is shown in UI

---


## Future Improvements

*  Authentication system
*  Chat history database
*  Add more models (Claude, Gemini, etc.)
*  Voice support
*  Cloud deployment

---

##  Tech Stack

* Python
* Flask
* HTML, CSS
* AI APIs


## 📄 License

MIT License

---

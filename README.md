#  Relay — Multi-Model AI Chat

**[-> Live demo: multi-model-chat-2wr1.onrender.com](https://multi-model-chat-2wr1.onrender.com)**
*(Free-tier hosting — first load after inactivity can take ~30–50s to wake up. Enter any name to sign in, no signup required.)*

One chat window, three models — Relay reads each message and routes it to the
model best suited for the job, instead of sending everything to a single
general-purpose model.

---

## Why this exists

Most simple chatbot demos wrap a single LLM. Relay routes each query to a
different backend model based on *what kind of task it is*, with an automatic
fallback if a provider is down — a small-scale version of the routing logic
production LLM systems actually use to balance cost, latency, and quality.

| Query type | Routed to | Why |
|---|---|---|
| Reasoning (math, proofs, "step by step") | `deepseek-r1` via GitHub Models | Stronger step-by-step reasoning |
| Quick asks ("tl;dr", "summary", "brief") | `gpt-4o-mini` via GitHub Models | Fast, cheap, good enough |
| Everything else | `llama-3.3-70b-versatile` via Groq | Best general-purpose quality available |
| Any failure above | `llama-3.1-8b-instant` via Groq | Always-on fallback so the chat never just breaks |

---

## Screenshots

<p align="center">
  <img src="output/multi-model-chat1.png" width="32%" />
  <img src="output/multi-model-chat 2.png" width="32%" />
  <img src="output/multi-model-chat 3.png" width="32%" />
</p>

---

## Tech stack

- **Backend:** Python, Flask, Gunicorn
- **Model providers:** GitHub Models inference API, Groq API (via the `openai` SDK's chat-completions interface)
- **Frontend:** HTML, CSS, vanilla JS (no framework)
- **Deployment:** Render (Procfile-based)

---

## Project structure

```
Multi-model-chat/
├── app.py              # Flask app: routes, session-based sign-in, chat API
├── model_router.py      # Keyword-based routing + provider fallback logic
├── templates/
│   ├── index.html       # Chat UI
│   └── login.html        # Sign-in screen
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
├── Procfile              # gunicorn start command for deployment
└── .env.example         # Template for required environment variables
```

---

## Running it locally

```bash
git clone https://github.com/kalpana29-2005/Multi-model-chat.git
cd Multi-model-chat
python -m venv venv && venv\Scripts\activate      # optional
pip install -r requirements.txt
cp .env.example .env      # then fill in your own API keys
python app.py
```

Open `http://127.0.0.1:5000`.

You'll need your own free API keys to run it:
- GitHub Models token → https://github.com/settings/tokens
- Groq API key → https://console.groq.com/keys

---

## Notes on the current implementation

This is a demo-scale project, and a couple of design choices are intentional
simplifications rather than oversights:

- **Sign-in is name-only, no password.** There's no real user account system —
  session is just a name. Good enough for a public demo, not meant to be
  production auth.
- **Chat history is stored in memory**, not a database, so it resets on every
  server restart/redeploy and won't scale across multiple instances. Swapping
  in SQLite/Postgres is the natural next step.

## Planned improvements

- [ ] Persistent chat history (SQLite/Postgres)
- [ ] Real authentication
- [ ] Add more model providers (Claude, Gemini)
- [ ] Voice input/output

---

## License

MIT License

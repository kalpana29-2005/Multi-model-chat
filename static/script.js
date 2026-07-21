// Relay — chat front end
// Talks to /api/chat, renders the conversation, and lights up the
// routing board to show which model answered each message.

const chatWindow = document.getElementById("chat-window");
const emptyState = document.getElementById("empty-state");
const composer = document.getElementById("composer");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const headerSignal = document.getElementById("header-signal");
const headerSignalLabel = document.getElementById("header-signal-label");
const routeNodes = document.querySelectorAll(".route-node");

const ROUTE_LABELS = {
  reasoning: "Reasoning",
  quick: "Quick",
  default: "Default",
  fallback: "Fallback",
};

// Map whatever label the backend returns to one of the four routes on
// the board, so the UI stays correct even if a model name changes.
function routeFromModelLabel(model) {
  if (!model) return "default";
  const m = model.toLowerCase();
  if (m.includes("fallback")) return "fallback";
  if (m.includes("deepseek")) return "reasoning";
  if (m.includes("gpt-4o-mini")) return "quick";
  if (m.includes("error")) return "fallback";
  return "default";
}

function setActiveRoute(route) {
  routeNodes.forEach((node) => {
    node.classList.toggle("active", node.dataset.route === route);
  });
  headerSignalLabel.textContent = ROUTE_LABELS[route] || "Idle";
}

function setSignalLive(isLive) {
  const dot = headerSignal.querySelector(".pulse-dot");
  dot.classList.toggle("live", isLive);
}

function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
}
input.addEventListener("input", autoGrow);

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendMessage({ role, text, model }) {
  if (emptyState) emptyState.remove();

  const bubble = document.createElement("div");
  bubble.className = `msg ${role === "user" ? "msg-user" : "msg-bot"}`;

  if (role === "assistant") {
    const route = routeFromModelLabel(model);
    const meta = document.createElement("div");
    meta.className = "msg-meta";
    meta.innerHTML = `<span class="dot dot-${route}"></span><span>${model || "model"}</span>`;
    bubble.appendChild(meta);
  }

  const body = document.createElement("div");
  body.textContent = text;
  bubble.appendChild(body);

  chatWindow.appendChild(bubble);
  scrollToBottom();
}

function appendTypingIndicator() {
  const bubble = document.createElement("div");
  bubble.className = "msg msg-bot";
  bubble.id = "typing-indicator";
  bubble.textContent = "…thinking";
  chatWindow.appendChild(bubble);
  scrollToBottom();
  return bubble;
}

async function sendMessage(text) {
  appendMessage({ role: "user", text });

  const guessedRoute = /solve|math|equation|logic|step by step|proof|derive/i.test(text)
    ? "reasoning"
    : /quick|fast|short|summary|tl;dr|brief/i.test(text)
    ? "quick"
    : "default";
  setActiveRoute(guessedRoute);
  setSignalLive(true);

  const typing = appendTypingIndicator();
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      appendMessage({ role: "assistant", text: data.error || "Something went wrong.", model: "error" });
      setActiveRoute("fallback");
    } else {
      appendMessage({ role: "assistant", text: data.reply, model: data.model });
      setActiveRoute(routeFromModelLabel(data.model));
    }
  } catch (err) {
    typing.remove();
    appendMessage({ role: "assistant", text: "Network error — is the Flask server running?", model: "error" });
    setActiveRoute("fallback");
  } finally {
    setSignalLive(false);
    sendBtn.disabled = false;
  }
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  autoGrow();
  sendMessage(text);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});

clearBtn.addEventListener("click", async () => {
  await fetch("/api/clear", { method: "POST" });
  chatWindow.innerHTML = "";
  const el = document.createElement("div");
  el.className = "empty-state";
  el.id = "empty-state";
  el.innerHTML = "<p>Conversation cleared. Ask anything to start a new one.</p>";
  chatWindow.appendChild(el);
  setActiveRoute(null);
});

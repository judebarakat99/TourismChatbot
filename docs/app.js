// ✅ Set this to your backend URL.
// Local testing:
// const BACKEND_URL = "http://localhost:8000";
//
// Production (after you deploy backend somewhere public):
// const BACKEND_URL = "https://YOUR-BACKEND-DOMAIN";
const BACKEND_URL = "http://localhost:8000";

const sessionId = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now());

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const langEl = document.getElementById("language");
const sourcesListEl = document.getElementById("sourcesList");
const statusEl = document.getElementById("status");

function setStatus(text) {
  statusEl.textContent = text;
}

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msgRow ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  chatEl.appendChild(row);
  chatEl.scrollTop = chatEl.scrollHeight;

  return bubble;
}

function setSources(sources) {
  sourcesListEl.innerHTML = "";
  (sources || []).forEach((s, i) => {
    const li = document.createElement("li");
    const title = s.title || "source";
    const src = s.source || "";
    li.textContent = `[${i + 1}] ${title}${src ? " — " + src : ""}`;
    sourcesListEl.appendChild(li);
  });
}

// Basic SSE chunk parser for "event: X\ndata: Y\n\n"
function parseSSE(buffer) {
  const events = [];
  let idx;
  while ((idx = buffer.indexOf("\n\n")) !== -1) {
    const raw = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 2);

    let eventName = "message";
    const dataLines = [];

    raw.split("\n").forEach((line) => {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
    });

    const data = dataLines.join("\n").replace(/\\n/g, "\n");
    events.push({ event: eventName, data });
  }
  return { events, buffer };
}

async function pingHealth() {
  try {
    const r = await fetch(`${BACKEND_URL}/health`);
    if (!r.ok) throw new Error(`health status ${r.status}`);
    setStatus("Connected ✅");
  } catch (e) {
    setStatus("Not connected ❌");
  }
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = "";
  sendBtn.disabled = true;
  setSources([]);
  addMessage("user", text);

  const assistantBubble = addMessage("assistant", "");
  setStatus("Streaming…");

  try {
    const res = await fetch(`${BACKEND_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        language: langEl.value,
      }),
    });

    if (!res.ok || !res.body) {
      const bodyText = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${bodyText}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parsed = parseSSE(buffer);
      buffer = parsed.buffer;

      for (const ev of parsed.events) {
        if (ev.event === "meta") {
          try {
            const meta = JSON.parse(ev.data);
            setSources(meta.sources || []);
          } catch {}
        } else if (ev.event === "token") {
          assistantBubble.textContent += ev.data;
          chatEl.scrollTop = chatEl.scrollHeight;
        } else if (ev.event === "done") {
          setStatus("Connected ✅");
        }
      }
    }

    setStatus("Connected ✅");
  } catch (err) {
    console.error(err);
    assistantBubble.textContent =
      "Error: Could not reach backend. Check BACKEND_URL and CORS settings.\n\n" +
      String(err);
    setStatus("Not connected ❌");
  } finally {
    sendBtn.disabled = false;
  }
}

// Enter to send, Shift+Enter for newline
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener("click", sendMessage);

// Initial message + health ping
addMessage("assistant", "Hi! Ask me anything about UK travel (itineraries, transport, seasons, festivals, etiquette).");
pingHealth();

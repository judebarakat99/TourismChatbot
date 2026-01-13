// Change this when backend is deployed publicly
const BACKEND_URL = "http://localhost:8000";

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const lang = document.getElementById("language");
const statusEl = document.getElementById("status");
const sourcesList = document.getElementById("sourcesList");

const sessionId = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now());

function setStatus(t) { statusEl.textContent = t; }

function add(role, text) {
  const row = document.createElement("div");
  row.className = "msg " + (role === "user" ? "user" : "bot");
  const b = document.createElement("div");
  b.className = "bubble";
  b.textContent = text;
  row.appendChild(b);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return b;
}

function setSources(sources) {
  sourcesList.innerHTML = "";
  (sources || []).forEach((s, i) => {
    const li = document.createElement("li");
    li.textContent = `[${i + 1}] ${s.title || "source"} — ${s.source || ""}`;
    sourcesList.appendChild(li);
  });
}

// Parse SSE response chunks: event: X \n data: Y \n\n
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

async function ping() {
  try {
    const r = await fetch(`${BACKEND_URL}/health`);
    setStatus(r.ok ? "Connected ✅" : "Not connected ❌");
  } catch {
    setStatus("Not connected ❌");
  }
}

async function send() {
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  sendBtn.disabled = true;
  setSources([]);

  add("user", text);
  const botBubble = add("assistant", "");
  setStatus("Streaming…");

  try {
    const res = await fetch(`${BACKEND_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        language: lang.value,
      }),
    });

    if (!res.ok || !res.body) {
      const t = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${t}`);
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
            setSources(JSON.parse(ev.data).sources || []);
          } catch {}
        }
        if (ev.event === "token") {
          botBubble.textContent += ev.data;
          chat.scrollTop = chat.scrollHeight;
        }
        if (ev.event === "done") {
          setStatus("Connected ✅");
        }
      }
    }

    setStatus("Connected ✅");
  } catch (e) {
    console.error(e);
    botBubble.textContent =
      "Error connecting to backend.\n\n" + String(e) +
      "\n\nFix: Set BACKEND_URL correctly and allow GitHub Pages origin in CORS.";
    setStatus("Not connected ❌");
  } finally {
    sendBtn.disabled = false;
  }
}

// Enter sends, Shift+Enter newline
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
sendBtn.addEventListener("click", send);

add("assistant", "Hi! Ask me about UK travel. Example: “Plan a 3-day London itinerary.”");
ping();

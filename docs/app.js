// ✅ CHANGE THIS to your deployed backend URL (Render/Railway/Azure/etc)
const BACKEND_URL = "https://YOUR-BACKEND-DOMAIN";

// simple client session id
const sessionId = (crypto.randomUUID && crypto.randomUUID()) || ("sess_" + Math.random().toString(16).slice(2) + "_" + Date.now());

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const langEl = document.getElementById("language");
const sourcesListEl = document.getElementById("sourcesList");

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
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
  (sources || []).forEach((s, idx) => {
    const li = document.createElement("li");
    const label = `[${idx + 1}] ${s.title} — ${s.source}`;
    if (s.url) {
      const a = document.createElement("a");
      a.href = s.url;
      a.target = "_blank";
      a.rel = "noreferrer";
      a.textContent = label + " (link)";
      li.appendChild(a);
    } else {
      li.textContent = label;
    }
    sourcesListEl.appendChild(li);
  });
}

// Parse SSE text/event-stream (messages separated by blank line)
function parseSSEChunk(buffer) {
  const events = [];
  let idx;
  while ((idx = buffer.indexOf("\n\n")) !== -1) {
    const raw = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 2);

    let event = "message";
    let dataLines = [];
    for (const line of raw.split("\n")) {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
    }
    const data = dataLines.join("\n").replace(/\\n/g, "\n");
    events.push({ event, data });
  }
  return { events, buffer };
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = "";
  setSources([]);

  addMessage("user", text);
  const assistantBubble = addMessage("assistant", "");

  sendBtn.disabled = true;
  sendBtn.textContent = "Streaming…";

  try {
    const res = await fetch(`${BACKEND_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        language: langEl.value
      })
    });

    if (!res.ok || !res.body) {
      const err = await res.text();
      throw new Error(err || `HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parsed = parseSSEChunk(buffer);
      buffer = parsed.buffer;

      for (const ev of parsed.events) {
        if (ev.event === "meta") {
          try {
            const obj = JSON.parse(ev.data);
            if (obj && obj.sources) setSources(obj.sources);
          } catch {}
        }
        if (ev.event === "token") {
          assistantBubble.textContent += ev.data;
          chatEl.scrollTop = chatEl.scrollHeight;
        }
        if (ev.event === "done") {
          break;
        }
      }
    }
  } catch (e) {
    assistantBubble.textContent = "Error: " + (e?.message || e);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
  }
}

sendBtn.addEventListener("click", send);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});

// welcome message
addMessage("assistant", "Hi! Ask me about UK attractions, events, transport, food, and itinerary ideas.");

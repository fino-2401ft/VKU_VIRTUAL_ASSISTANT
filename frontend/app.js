const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chatForm");
const inputEl = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const suggestionsEl = document.getElementById("suggestions");
const healthBadge = document.getElementById("healthBadge");

const SESSION_KEY = "vku_va_session_id";
let sessionId = localStorage.getItem(SESSION_KEY) || null;
let busy = false;

function addMessage(role, text, meta = null) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);

  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "meta";
    if (meta.category) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = meta.category;
      metaEl.appendChild(chip);
    }
    if (typeof meta.confidence === "number" && meta.confidence > 0) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = `Độ tin cậy ~ ${Math.round(meta.confidence * 100)}%`;
      metaEl.appendChild(chip);
    }
    (meta.sources || []).slice(0, 3).forEach((s) => {
      const chip = document.createElement("span");
      chip.className = "chip source";
      chip.textContent = s.file || s.title || "source";
      metaEl.appendChild(chip);
    });
    if (metaEl.childNodes.length) wrap.appendChild(metaEl);
  }

  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(state) {
  busy = state;
  sendBtn.disabled = state;
  inputEl.disabled = state;
}

async function sendMessage(text) {
  const message = (text || "").trim();
  if (!message || busy) return;

  addMessage("user", message);
  inputEl.value = "";
  setBusy(true);

  const typing = document.createElement("div");
  typing.className = "msg bot";
  typing.id = "typing";
  typing.innerHTML = '<div class="bubble typing">Đang tìm trong tài liệu demo…</div>';
  messagesEl.appendChild(typing);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    sessionId = data.session_id;
    localStorage.setItem(SESSION_KEY, sessionId);

    document.getElementById("typing")?.remove();
    addMessage("bot", data.answer, {
      category: data.category,
      confidence: data.confidence,
      sources: data.sources,
    });
  } catch (err) {
    document.getElementById("typing")?.remove();
    addMessage(
      "bot",
      "Không gọi được API. Hãy chắc backend đang chạy (uvicorn) rồi thử lại."
    );
    console.error(err);
  } finally {
    setBusy(false);
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(inputEl.value);
});

async function boot() {
  addMessage(
    "bot",
    "Xin chào! Mình là trợ lý ảo demo của VKU. Bạn có thể hỏi về học phí, quy chế, tuyển sinh… hoặc bấm câu hỏi gợi ý bên trái."
  );

  try {
    const health = await fetch("/api/health").then((r) => r.json());
    healthBadge.textContent = `API OK · ${health.faq_items} FAQ`;
  } catch {
    healthBadge.textContent = "API offline";
  }

  try {
    const data = await fetch("/api/suggestions").then((r) => r.json());
    suggestionsEl.innerHTML = "";
    (data.suggestions || []).forEach((q) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "suggestion";
      btn.textContent = q;
      btn.addEventListener("click", () => sendMessage(q));
      suggestionsEl.appendChild(btn);
    });
  } catch {
    suggestionsEl.textContent = "Không tải được gợi ý.";
  }
}

boot();

let currentSessionId = null;
const CHAT_SESSION_STORAGE_KEY = "current_chat_session_id";
const CHAT_PENDING_REQUEST_STORAGE_KEY = "current_chat_pending_request";
const AI_TYPING_DELAY_MS = 2000;
const CHAT_RESUME_POLL_MS = 1500;
const CHAT_RESUME_TIMEOUT_MS = 30000;

function persistCurrentSessionId() {
  if (currentSessionId) {
    sessionStorage.setItem(CHAT_SESSION_STORAGE_KEY, String(currentSessionId));
  } else {
    sessionStorage.removeItem(CHAT_SESSION_STORAGE_KEY);
  }
}

function restoreStoredSessionId() {
  const stored = sessionStorage.getItem(CHAT_SESSION_STORAGE_KEY);
  currentSessionId = stored ? Number(stored) : null;
}

function getRenderedMessageCount() {
  return document.querySelectorAll("#chat-messages > div").length;
}

function setPendingRequestState(payload) {
  sessionStorage.setItem(CHAT_PENDING_REQUEST_STORAGE_KEY, JSON.stringify(payload));
}

function getPendingRequestState() {
  const raw = sessionStorage.getItem(CHAT_PENDING_REQUEST_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error("Falha ao restaurar estado pendente do chat:", error);
    sessionStorage.removeItem(CHAT_PENDING_REQUEST_STORAGE_KEY);
    return null;
  }
}

function clearPendingRequestState() {
  sessionStorage.removeItem(CHAT_PENDING_REQUEST_STORAGE_KEY);
}

function ensureHistoryState() {
  const history = document.getElementById("chat-history");
  if (!history || history.children.length > 0) return;

  history.innerHTML = `
    <div data-empty-history="true" class="rounded-[1.4rem] border border-dashed border-[#d9e3f5] bg-[#fbfdff] p-4 text-sm leading-6 text-[#72809d]">
      Nenhuma interação ainda. Envie uma pergunta para começar a conversa e acompanhar os próximos passos da sessão.
    </div>
  `;
}

function appendHistory(role, content) {
  const history = document.getElementById("chat-history");
  history.querySelectorAll("[data-empty-history]").forEach((item) => item.remove());
  const item = document.createElement("div");
  item.className = "rounded-[1.2rem] border border-[#e7edf7] bg-[#fbfdff] p-3 text-sm shadow-sm";
  item.innerHTML = `
    <strong class="mb-1 block text-xs font-semibold uppercase tracking-[0.2em] text-[#7f8eab]">${role === "user" ? "Usuario" : "IA"}</strong>
    <span class="block leading-6 text-[#24324d]">${content}</span>
  `;
  history.prepend(item);
}

function clearChatPanels() {
  const history = document.getElementById("chat-history");
  const messages = document.getElementById("chat-messages");
  if (history) history.innerHTML = "";
  if (messages) messages.innerHTML = "";
}

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function appendMessage(role, content) {
  const messages = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "flex justify-end" : "flex justify-start";

  const bubble = document.createElement("div");
  bubble.className =
    role === "user"
      ? "max-w-[78%] rounded-[1.4rem] rounded-br-md bg-gradient-to-r from-[#3478f6] to-[#6c5ce7] px-4 py-3 text-sm leading-7 text-white shadow-[0_10px_24px_rgba(52,120,246,0.22)]"
      : "max-w-[78%] rounded-[1.4rem] rounded-bl-md border border-[#e3eaf6] bg-white px-4 py-3 text-sm leading-7 text-[#24324d] shadow-sm";
  bubble.textContent = content;

  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

function renderSessionMessages(messagesList) {
  clearChatPanels();
  messagesList.forEach((item) => {
    appendHistory(item.role, item.content);
    appendMessage(item.role, item.content);
  });
}

function appendTypingIndicator() {
  const messages = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = "flex justify-start";
  wrapper.dataset.typingIndicator = "true";

  const bubble = document.createElement("div");
  bubble.className =
    "inline-flex items-center rounded-[1.5rem] rounded-bl-md border border-[#e3eaf6] bg-white px-4 py-3 text-sm text-[#5f6f8c] shadow-sm";
  bubble.innerHTML = `
    <div class="chat-typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;

  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

function removeTypingIndicator() {
  document.querySelectorAll("[data-typing-indicator='true']").forEach((item) => item.remove());
}

async function sendChatMessage(message) {
  const previousMessageCount = getRenderedMessageCount();
  const pendingState = {
    message,
    sessionId: currentSessionId,
    previousMessageCount,
    startedAt: Date.now(),
  };

  appendHistory("user", message);
  appendMessage("user", message);
  appendTypingIndicator();
  setPendingRequestState(pendingState);

  const response = await fetch("/api/v1/chat/message", {
    method: "POST",
    headers: authHeaders(),
    keepalive: true,
    body: JSON.stringify({ message, session_id: currentSessionId }),
  });

  await wait(AI_TYPING_DELAY_MS);
  removeTypingIndicator();

  if (!response.ok) {
    let errorMessage = "Nao foi possivel processar a mensagem.";
    try {
      const errorPayload = await response.json();
      if (errorPayload?.detail) {
        errorMessage = typeof errorPayload.detail === "string" ? errorPayload.detail : JSON.stringify(errorPayload.detail);
      }
    } catch (error) {
      console.error("Falha ao ler erro do chat:", error);
    }
    clearPendingRequestState();
    appendMessage("assistant", errorMessage);
    return;
  }

  const data = await response.json();
  currentSessionId = data.session_id;
  persistCurrentSessionId();
  clearPendingRequestState();
  appendHistory("assistant", data.answer.summary);
  appendMessage("assistant", data.answer.summary);
}

async function loadCurrentSession() {
  restoreStoredSessionId();
  const response = await fetch("/api/v1/chat/session/current", {
    headers: authHeaders(),
  });

  if (!response.ok) {
    ensureHistoryState();
    return;
  }

  const data = await response.json();
  if (!data.session_id || !Array.isArray(data.messages) || data.messages.length === 0) {
    currentSessionId = data.session_id || currentSessionId;
    persistCurrentSessionId();
    ensureHistoryState();
    return;
  }

  currentSessionId = data.session_id;
  persistCurrentSessionId();
  renderSessionMessages(data.messages);
}

async function pollPendingRequestUntilResolved() {
  const pendingState = getPendingRequestState();
  if (!pendingState) return;

  const loading = document.getElementById("chat-loading");
  const startedAt = pendingState.startedAt || Date.now();
  loading.textContent = "Retomando resposta em andamento...";

  const hasPendingUserMessageInUi = Array.from(document.querySelectorAll("#chat-messages > div"))
    .some((item) => item.textContent?.includes(pendingState.message));

  if (!hasPendingUserMessageInUi) {
    appendHistory("user", pendingState.message);
    appendMessage("user", pendingState.message);
  }

  appendTypingIndicator();

  while (Date.now() - startedAt < CHAT_RESUME_TIMEOUT_MS) {
    const response = await fetch("/api/v1/chat/session/current", {
      headers: authHeaders(),
    });

    if (response.ok) {
      const data = await response.json();
      const messages = Array.isArray(data.messages) ? data.messages : [];
      const hasAssistantReply = messages.length >= (pendingState.previousMessageCount || 0) + 2
        && messages[messages.length - 1]?.role === "assistant";

      if (hasAssistantReply) {
        currentSessionId = data.session_id || currentSessionId;
        persistCurrentSessionId();
        clearPendingRequestState();
        removeTypingIndicator();
        loading.textContent = "";
        renderSessionMessages(messages);
        return;
      }
    }

    await wait(CHAT_RESUME_POLL_MS);
  }

  removeTypingIndicator();
  loading.textContent = "";
}

document.getElementById("chat-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();

  if (!message) return;

  input.value = "";
  await sendChatMessage(message);
  input.focus();
});

window.addEventListener("load", async () => {
  await loadCurrentSession();
  ensureHistoryState();
  await pollPendingRequestUntilResolved();
  const pendingMessage = sessionStorage.getItem("pending_chat_message");
  if (!pendingMessage) return;

  sessionStorage.removeItem("pending_chat_message");
  await sendChatMessage(pendingMessage);
});

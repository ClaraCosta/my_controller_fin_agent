let currentSessionId = null;

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

async function sendChatMessage(message) {
  const loading = document.getElementById("chat-loading");

  appendHistory("user", message);
  appendMessage("user", message);
  loading.textContent = "Consultando dados do sistema...";

  const response = await fetch("/api/v1/chat/message", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ message, session_id: currentSessionId }),
  });

  loading.textContent = "";

  if (!response.ok) {
    appendMessage("assistant", "Nao foi possivel processar a mensagem.");
    return;
  }

  const data = await response.json();
  currentSessionId = data.session_id;
  appendHistory("assistant", data.answer.summary);
  appendMessage("assistant", data.answer.summary);
}

document.getElementById("chat-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();

  if (!message) return;

  await sendChatMessage(message);
  input.value = "";
});

window.addEventListener("load", async () => {
  ensureHistoryState();
  const pendingMessage = sessionStorage.getItem("pending_chat_message");
  if (!pendingMessage) return;

  sessionStorage.removeItem("pending_chat_message");
  await sendChatMessage(pendingMessage);
});

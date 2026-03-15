let currentSessionId = null;

function appendHistory(role, content) {
  const history = document.getElementById("chat-history");
  const item = document.createElement("div");
  item.className = "rounded-2xl border border-slate-200 p-3 text-sm";
  item.innerHTML = `<strong class="block mb-1 capitalize">${role}</strong><span>${content}</span>`;
  history.prepend(item);
}

function appendMessage(role, content) {
  const messages = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "flex justify-end" : "flex justify-start";

  const bubble = document.createElement("div");
  bubble.className =
    role === "user"
      ? "max-w-[78%] rounded-[1.4rem] rounded-br-md bg-slate-900 px-4 py-3 text-sm leading-7 text-white shadow-sm"
      : "max-w-[78%] rounded-[1.4rem] rounded-bl-md border border-slate-200 bg-white px-4 py-3 text-sm leading-7 text-slate-700 shadow-sm";
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
  const pendingMessage = sessionStorage.getItem("pending_chat_message");
  if (!pendingMessage) return;

  sessionStorage.removeItem("pending_chat_message");
  await sendChatMessage(pendingMessage);
});

let currentSessionId = null;

function appendHistory(role, content) {
  const history = document.getElementById("chat-history");
  const item = document.createElement("div");
  item.className = "rounded-2xl border border-slate-200 p-3 text-sm";
  item.innerHTML = `<strong class="block mb-1 capitalize">${role}</strong><span>${content}</span>`;
  history.prepend(item);
}

document.getElementById("chat-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const loading = document.getElementById("chat-loading");
  const responseBox = document.getElementById("chat-response");
  const message = input.value.trim();

  if (!message) return;

  appendHistory("user", message);
  loading.textContent = "Consultando dados do sistema...";

  const response = await fetch("/api/v1/chat/message", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ message, session_id: currentSessionId }),
  });

  loading.textContent = "";

  if (!response.ok) {
    responseBox.textContent = "Nao foi possivel processar a mensagem.";
    return;
  }

  const data = await response.json();
  currentSessionId = data.session_id;
  responseBox.innerHTML = `
    <h3 class="text-lg font-bold">Resumo</h3>
    <p class="mt-2">${data.answer.summary}</p>
    <h4 class="mt-4 text-sm font-semibold uppercase tracking-wide text-slate-500">Pontos principais</h4>
    <ul class="mt-2 list-disc pl-5">
      ${data.answer.data_points.map((item) => `<li>${item}</li>`).join("")}
    </ul>
    <p class="mt-4 text-xs uppercase tracking-wide text-sky-700">Fonte: ${data.answer.source}</p>
  `;
  appendHistory("assistant", data.answer.summary);
  input.value = "";
});


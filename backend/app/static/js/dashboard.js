async function loadDashboard() {
  const response = await fetch("/api/v1/dashboard", { headers: authHeaders() });
  if (!response.ok) {
    window.location.href = "/";
    return;
  }

  const data = await response.json();
  const cards = [
    ["Clientes", data.total_clients],
    ["Contatos", data.total_contacts],
    ["Solicitações", data.total_requests],
    ["Prioridades recentes", data.recent_priorities.join(", ") || "Sem dados"],
  ];

  const container = document.getElementById("dashboard-cards");
  container.innerHTML = cards
    .map(([label, value]) => `<article class="card"><p class="text-sm text-slate-500">${label}</p><h3 class="mt-3 text-3xl font-black">${value}</h3></article>`)
    .join("");
}

loadDashboard();


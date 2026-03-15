function redirectToCentralChat(message) {
  if (!message) return;
  sessionStorage.setItem("pending_chat_message", message);
  window.location.href = "/chat";
}

async function loadDashboard() {
  const response = await fetch("/api/v1/dashboard", { headers: authHeaders() });
  if (!response.ok) {
    window.location.href = "/";
    return;
  }

  const data = await response.json();
  const cards = [
    {
      label: "Clientes",
      value: data.total_clients,
      accent: "linear-gradient(135deg, #dff4ef, #eefcf9)",
      icon: "fa-solid fa-user",
      color: "#10b981",
    },
    {
      label: "Contatos",
      value: data.total_contacts,
      accent: "linear-gradient(135deg, #ffe9e5, #fff6f4)",
      icon: "fa-solid fa-address-book",
      color: "#ff6b57",
    },
    {
      label: "Solicitacoes",
      value: data.total_requests,
      accent: "linear-gradient(135deg, #e7efff, #f4f7ff)",
      icon: "fa-solid fa-folder-open",
      color: "#3478f6",
    },
  ];

  const container = document.getElementById("dashboard-cards");
  container.innerHTML = cards
    .map(
      (card) => `
        <article class="rounded-[1.8rem] border border-[#e6ebf4] p-5 shadow-sm" style="background: ${card.accent};">
          <div class="flex items-center justify-between">
            <p class="text-sm font-semibold text-[#51607d]">${card.label}</p>
            <span class="flex h-[4.5rem] w-[4.5rem] items-center justify-center rounded-[1.5rem]" style="background: ${card.color}20; color: ${card.color};">
              <i class="${card.icon} text-[1.9rem]"></i>
            </span>
          </div>
          <h3 class="mt-4 text-3xl font-black tracking-tight text-[#1f2a44]">${card.value}</h3>
          <p class="mt-3 text-sm font-medium" style="color: ${card.color};">Indicador operacional do workspace</p>
        </article>
      `
    )
    .join("");
}

function initClientsTable() {
  $("#clients-table").DataTable({
    processing: true,
    serverSide: true,
    searching: true,
    lengthChange: true,
    pageLength: 10,
    ajax: function (data, callback) {
      const params = new URLSearchParams();
      params.set("draw", data.draw);
      params.set("start", data.start);
      params.set("length", data.length);
      params.set("search[value]", data.search?.value || "");

      fetch(`/api/v1/clients/datatable?${params.toString()}`, {
        headers: authHeaders({ Accept: "application/json" }),
      })
        .then(async (response) => {
          if (!response.ok) {
            const body = await response.text();
            throw new Error(`HTTP ${response.status}: ${body}`);
          }
          return response.json();
        })
        .then((payload) => {
          const tableWrap = document.querySelector(".dashboard-table-wrap");
          if (tableWrap) {
            tableWrap.removeAttribute("data-error");
          }
          callback(payload);
        })
        .catch((error) => {
          console.error("DataTable fetch error:", error);
          callback({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
          const tableWrap = document.querySelector(".dashboard-table-wrap");
          if (tableWrap) {
            tableWrap.setAttribute("data-error", "Nao foi possivel carregar a tabela de clientes.");
          }
        });
    },
    columns: [
      {
        data: "id",
        orderable: false,
        searchable: false,
        render: function () {
          return `<input type="checkbox" class="h-4 w-4 rounded border-slate-300" />`;
        },
      },
      {
        data: "name",
        render: function (data, _, row) {
          return `
            <div class="flex items-center gap-3 min-w-[260px]">
              <span class="flex h-12 w-12 items-center justify-center rounded-full bg-[#edf3ff] font-bold text-[#4f7af7]">${row.initial}</span>
              <div>
                <p class="font-semibold text-[#31415f]">${data}</p>
                <p class="mt-1 text-sm text-[#7a88a3]">${row.primary_contact_name} • ${row.primary_contact_role}</p>
              </div>
            </div>
          `;
        },
      },
      {
        data: "status",
        render: function (data) {
          const tone = data === "active" ? "bg-[#e9fbf2] text-[#16a765]" : "bg-[#fff3ea] text-[#e07a24]";
          return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tone}">${data}</span>`;
        },
      },
      { data: "primary_contact_phone" },
      { data: "primary_contact_email" },
      { data: "document_number" },
      {
        data: "id",
        orderable: false,
        searchable: false,
        render: function () {
          return `<button class="rounded-full px-3 py-1 text-xl font-bold text-[#4f7af7]">⋯</button>`;
        },
      },
    ],
    order: [[1, "asc"]],
    language: {
      processing: "Carregando...",
      search: "Buscar:",
      lengthMenu: "Mostrar _MENU_ registros",
      info: "Mostrando _START_ a _END_ de _TOTAL_ clientes",
      infoEmpty: "Nenhum cliente encontrado",
      zeroRecords: "Nenhum resultado localizado",
      paginate: {
        first: "Primeira",
        last: "Ultima",
        next: "Proxima",
        previous: "Anterior",
      },
    },
  });
}

async function handleDashboardChat(event) {
  event.preventDefault();
  const input = document.getElementById("dashboard-chat-input");
  const message = input.value.trim();

  if (!message) return;
  redirectToCentralChat(message);
}

loadDashboard();
document.getElementById("dashboard-chat-form")?.addEventListener("submit", handleDashboardChat);
document.querySelectorAll("[data-chat-shortcut]").forEach((button) => {
  button.addEventListener("click", () => {
    redirectToCentralChat(button.getAttribute("data-chat-shortcut"));
  });
});
if (window.jQuery && $("#clients-table").length) {
  initClientsTable();
}

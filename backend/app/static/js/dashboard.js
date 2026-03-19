function redirectToCentralChat(message) {
  if (!message) return;
  sessionStorage.setItem("pending_chat_message", message);
  window.location.href = "/chat";
}

let clientsTable = null;
let mainDashboardChart = null;
let donutDashboardChart = null;

function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function resetClientForm() {
  document.getElementById("client-form")?.reset();
  document.getElementById("client-id").value = "";
  document.getElementById("client-modal-title").textContent = "Novo cliente";
  document.getElementById("client-form-feedback").textContent = "";
  document.getElementById("client-status").value = "active";
}

function formatCNPJ(value) {
  const digits = value.replace(/\D/g, "").slice(0, 14);
  return digits
    .replace(/^(\d{2})(\d)/, "$1.$2")
    .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})(\d)/, ".$1/$2")
    .replace(/(\d{4})(\d)/, "$1-$2");
}

function attachClientDocumentMask() {
  const input = document.getElementById("client-document-number");
  if (!input) return;

  input.addEventListener("input", () => {
    input.value = formatCNPJ(input.value);
  });
}

function getClientPayload() {
  return {
    name: document.getElementById("client-name").value.trim(),
    document_number: document.getElementById("client-document-number").value.trim(),
    status: document.getElementById("client-status").value,
    primary_contact_name: document.getElementById("client-primary-contact-name").value.trim() || null,
    primary_contact_role: document.getElementById("client-primary-contact-role").value.trim() || null,
    primary_contact_email: document.getElementById("client-primary-contact-email").value.trim() || null,
    primary_contact_phone: document.getElementById("client-primary-contact-phone").value.trim() || null,
  };
}

function fillClientForm(client) {
  document.getElementById("client-id").value = client.id;
  document.getElementById("client-modal-title").textContent = "Editar cliente";
  document.getElementById("client-name").value = client.name || "";
  document.getElementById("client-document-number").value = client.document_number || "";
  document.getElementById("client-status").value = client.status || "active";
  document.getElementById("client-primary-contact-name").value = client.primary_contact_name || "";
  document.getElementById("client-primary-contact-role").value = client.primary_contact_role || "";
  document.getElementById("client-primary-contact-email").value = client.primary_contact_email || "";
  document.getElementById("client-primary-contact-phone").value = client.primary_contact_phone || "";
}

async function openEditClient(clientId) {
  const response = await fetch(`/api/v1/clients/${clientId}`, {
    headers: authHeaders({ Accept: "application/json" }),
  });

  if (!response.ok) return;

  const client = await response.json();
  resetClientForm();
  fillClientForm(client);
  openModal("client-modal");
}

async function deleteClient(clientId) {
  const confirmed = window.confirm("Deseja realmente excluir este cliente?");
  if (!confirmed) return;

  const response = await fetch(`/api/v1/clients/${clientId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (response.ok) {
    clientsTable?.ajax.reload(null, false);
  }
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
      accent: "linear-gradient(135deg, #ffffff, #f8fbff)",
      icon: "fa-solid fa-user",
      color: "#3478f6",
      helper: "Carteira principal",
      trend: `${Math.max(0, data.total_clients)} total`,
      trendTone: "bg-[#eaf2ff] text-[#3478f6]",
      footerLabel: "Base ativa",
      footerValue: Math.max(0, data.total_clients),
      chart: [34, 22, 58, 41, 73, 52, 64],
    },
    {
      label: "Contatos",
      value: data.total_contacts,
      accent: "linear-gradient(135deg, #ffffff, #fff9f7)",
      icon: "fa-solid fa-address-book",
      color: "#ff7a59",
      helper: "Rede operacional",
      trend: `${Math.max(0, data.total_contacts)} total`,
      trendTone: "bg-[#fff0ea] text-[#ff7a59]",
      footerLabel: "Cobertura atual",
      footerValue: Math.max(0, data.total_contacts),
      chart: [16, 28, 24, 37, 32, 44],
    },
    {
      label: "Solicitacoes",
      value: data.total_requests,
      accent: "linear-gradient(135deg, #ffffff, #f6f8ff)",
      icon: "fa-solid fa-folder-open",
      color: "#3478f6",
      helper: "Fluxo de atendimento",
      trend: `${Math.max(0, data.total_requests)} total`,
      trendTone: "bg-[#edf3ff] text-[#476be8]",
      footerLabel: "Volume operacional",
      footerValue: Math.max(0, data.total_requests),
      chart: [20, 36, 29, 52, 39, 46],
    },
  ];

  const container = document.getElementById("dashboard-cards");
  container.innerHTML = cards
    .map(
      (card) => `
        <article class="dashboard-stat-card flex h-full min-h-[18rem] flex-col rounded-[1.8rem] border border-[#e6ebf4] p-5 shadow-sm" style="background: ${card.accent}; --stat-color: ${card.color};">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold text-[#51607d]">${card.label}</p>
            </div>
            <span class="flex h-[0.5rem] w-[4.5rem] shrink-0 items-center justify-center rounded-[1.5rem]" style="background: ${card.color}18; color: ${card.color};">
              <i class="${card.icon} text-[2rem]"></i>
            </span>
          </div>
          <div class="mt-5 flex flex-1 items-end justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#91a0ba]">${card.helper}</p>
              <h3 class="mt-2 text-4xl font-black tracking-tight text-[#1f2a44]">${card.value}</h3>
              <div class="mt-3 inline-flex rounded-xl px-3 py-2 text-xs font-semibold ${card.trendTone}">${card.trend}</div>
            </div>
            <div class="dashboard-stat-mini-chart">
              ${card.chart
                .map(
                  (point, index) =>
                    `<span class="${index === card.chart.length - 2 ? "is-accent" : ""}" style="height:${point}px"></span>`
                )
                .join("")}
            </div>
          </div>
          <div class="mt-5 flex items-center justify-between rounded-[1.2rem] bg-white/80 px-4 py-3">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-xl" style="background:${card.color}14; color:${card.color};">
                <i class="${card.icon} text-sm"></i>
              </span>
              <div>
                <p class="text-sm font-semibold text-[#24324d]">${card.footerLabel}</p>
                <p class="text-xs text-[#7f8da8]">Indicador resumido da base</p>
              </div>
            </div>
            <p class="text-xl font-black text-[#24324d]">${card.footerValue}</p>
          </div>
        </article>
      `
    )
    .join("");

  renderDashboardCharts(data);
}

function renderDashboardCharts(data) {
  const mainChartElement = document.getElementById("dashboard-main-chart");
  const donutChartElement = document.getElementById("dashboard-donut-chart");

  if (mainDashboardChart) {
    mainDashboardChart.destroy();
  }
  if (donutDashboardChart) {
    donutDashboardChart.destroy();
  }

  if (window.ApexCharts && mainChartElement) {
    mainDashboardChart = new ApexCharts(mainChartElement, {
      chart: {
        type: "area",
        height: 360,
        toolbar: { show: false },
        zoom: { enabled: false },
        fontFamily: "Segoe UI, sans-serif",
      },
      colors: ["#3478f6", "#52b7f6", "#6c5ce7", "#ff7a59"],
      series: data.trend_series,
      stroke: {
        curve: "smooth",
        width: 3,
      },
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.28,
          opacityTo: 0.04,
          stops: [0, 95, 100],
        },
      },
      dataLabels: { enabled: false },
      legend: {
        position: "top",
        horizontalAlign: "left",
        labels: { colors: "#60708d" },
      },
      grid: {
        borderColor: "#e7edf8",
        strokeDashArray: 5,
      },
      xaxis: {
        categories: data.trend_labels,
        labels: { style: { colors: "#8a98b1", fontSize: "12px" } },
        axisBorder: { show: false },
        axisTicks: { show: false },
      },
      yaxis: {
        min: 0,
        forceNiceScale: true,
        labels: { style: { colors: "#8a98b1", fontSize: "12px" } },
      },
      tooltip: {
        theme: "light",
        x: { show: true },
      },
    });
    mainDashboardChart.render();
  }

  if (window.ApexCharts && donutChartElement) {
    donutDashboardChart = new ApexCharts(donutChartElement, {
      chart: {
        type: "donut",
        height: 360,
        fontFamily: "Segoe UI, sans-serif",
      },
      series: data.donut_metrics.map((item) => item.value),
      labels: data.donut_metrics.map((item) => item.label),
      colors: ["#3478f6", "#ffb648", "#7c8ba4", "#ff7a59"],
      dataLabels: {
        enabled: false,
      },
      legend: {
        position: "bottom",
        fontSize: "13px",
        labels: { colors: "#60708d" },
        itemMargin: { horizontal: 12, vertical: 6 },
      },
      plotOptions: {
        pie: {
          donut: {
            size: "68%",
            labels: {
              show: true,
              name: {
                show: true,
                color: "#8a98b1",
                offsetY: 16,
              },
              value: {
                show: true,
                fontSize: "34px",
                fontWeight: 800,
                color: "#1f2a44",
                offsetY: -10,
                formatter: function (value) {
                  return String(value);
                },
              },
              total: {
                show: true,
                label: "Documentos",
                color: "#60708d",
                formatter: function (w) {
                  return String(w.globals.seriesTotals.reduce((acc, current) => acc + current, 0));
                },
              },
            },
          },
        },
      },
      stroke: {
        width: 0,
      },
      tooltip: {
        y: {
          formatter: function (value) {
            return `${value} registro(s)`;
          },
        },
      },
    });
    donutDashboardChart.render();
  }
}

function initClientsTable() {
  clientsTable = $("#clients-table").DataTable({
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
          const tones = {
            active: "bg-[#e9fbf2] text-[#16a765]",
            new: "bg-[#eef3ff] text-[#476be8]",
            review: "bg-[#fff3ea] text-[#e07a24]",
            inactive: "bg-[#f4f5f8] text-[#6b7280]",
          };
          const labels = {
            active: "Ativo",
            new: "Novo",
            review: "Em análise",
            inactive: "Inativo",
          };
          const tone = tones[data] || "bg-[#eef3ff] text-[#476be8]";
          const label = labels[data] || data;
          return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tone}">${label}</span>`;
        },
      },
      { data: "primary_contact_phone" },
      { data: "primary_contact_email" },
      { data: "document_number" },
      {
        data: "id",
        orderable: false,
        searchable: false,
        render: function (data) {
          return `
            <div class="flex items-center gap-3 text-[#4f7af7]">
              <button class="client-edit-btn" data-client-id="${data}" title="Editar"><i class="fa-solid fa-pen"></i></button>
              <button class="client-delete-btn text-[#e07a24]" data-client-id="${data}" title="Excluir"><i class="fa-solid fa-trash"></i></button>
            </div>
          `;
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

  $("#clients-table").on("click", ".client-edit-btn", function () {
    openEditClient(this.dataset.clientId);
  });

  $("#clients-table").on("click", ".client-delete-btn", function () {
    deleteClient(this.dataset.clientId);
  });
}

async function handleDashboardChat(event) {
  event.preventDefault();
  const input = document.getElementById("dashboard-chat-input");
  const message = input.value.trim();

  if (!message) return;
  redirectToCentralChat(message);
}

async function downloadConsolidatedReport() {
  const button = document.getElementById("download-consolidated-report");
  const originalText = button?.textContent;
  if (button) button.textContent = "Gerando PDF...";

  const response = await fetch("/api/v1/reports/consolidated.pdf", {
    headers: authHeaders({ Accept: "application/pdf" }),
  });

  if (!response.ok) {
    if (button && originalText) button.textContent = originalText;
    return;
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "relatorio-consolidado.pdf";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);

  if (button && originalText) button.textContent = originalText;
}

async function submitClientForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("client-form-feedback");
  const clientId = document.getElementById("client-id").value;
  const payload = getClientPayload();

  if (!payload.name) {
    feedback.textContent = "Informe o nome do cliente.";
    return;
  }

  if (payload.document_number.replace(/\D/g, "").length !== 14) {
    feedback.textContent = "Informe um CNPJ completo para salvar o cliente.";
    return;
  }

  feedback.textContent = "Salvando cliente...";

  const response = await fetch(clientId ? `/api/v1/clients/${clientId}` : "/api/v1/clients", {
    method: clientId ? "PUT" : "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    try {
      const errorPayload = await response.json();
      const detail = Array.isArray(errorPayload.detail)
        ? errorPayload.detail.map((item) => item.msg).join(" ")
        : errorPayload.detail;
      feedback.textContent = detail || "Não foi possível salvar o cliente.";
    } catch {
      feedback.textContent = "Não foi possível salvar o cliente.";
    }
    return;
  }

  closeModal("client-modal");
  resetClientForm();
  clientsTable?.ajax.reload(null, false);
}

loadDashboard();
attachClientDocumentMask();
document.getElementById("dashboard-chat-form")?.addEventListener("submit", handleDashboardChat);
document.getElementById("download-consolidated-report")?.addEventListener("click", downloadConsolidatedReport);
document.getElementById("client-form")?.addEventListener("submit", submitClientForm);
document.getElementById("open-client-modal")?.addEventListener("click", () => {
  resetClientForm();
  openModal("client-modal");
});
document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => closeModal(button.getAttribute("data-close-modal")));
});
document.querySelectorAll("[data-chat-shortcut]").forEach((button) => {
  button.addEventListener("click", () => {
    redirectToCentralChat(button.getAttribute("data-chat-shortcut"));
  });
});
if (window.jQuery && $("#clients-table").length) {
  initClientsTable();
}

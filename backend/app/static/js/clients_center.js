let clientsTable = null;
let clientsToastTimer = null;

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

function hideClientsToast() {
  const toast = document.getElementById("clients-toast");
  if (!toast) return;

  if (clientsToastTimer) {
    window.clearTimeout(clientsToastTimer);
    clientsToastTimer = null;
  }

  toast.classList.remove("opacity-100");
  toast.classList.add("opacity-0");
  window.setTimeout(() => {
    toast.classList.remove("flex");
    toast.classList.add("hidden");
  }, 300);
}

function showClientsToast(message, tone = "success") {
  const toast = document.getElementById("clients-toast");
  const toastCard = document.getElementById("clients-toast-card");
  const toastIcon = document.getElementById("clients-toast-icon");
  const toastTitle = document.getElementById("clients-toast-title");
  const toastMessage = document.getElementById("clients-toast-message");

  if (!toast || !toastCard || !toastIcon || !toastTitle || !toastMessage) return;

  const variants = {
    success: {
      title: "Sucesso",
      card: "border-[#d7e5ff] bg-white",
      icon: "bg-[#edf4ff] text-[#3478f6]",
      symbol: "fa-solid fa-circle-check",
    },
    error: {
      title: "Erro",
      card: "border-[#ffd8d1] bg-white",
      icon: "bg-[#fff1ee] text-[#dd6b4d]",
      symbol: "fa-solid fa-circle-exclamation",
    },
  };

  const selected = variants[tone] || variants.success;

  toastTitle.textContent = selected.title;
  toastMessage.textContent = message;
  toastCard.className = `flex w-full max-w-2xl items-start gap-4 rounded-[2rem] border px-7 py-6 shadow-[0_28px_80px_rgba(31,42,68,0.22)] ${selected.card}`;
  toastIcon.className = `mt-0.5 flex h-14 w-14 items-center justify-center rounded-[1.35rem] text-[1.2rem] ${selected.icon}`;
  toastIcon.innerHTML = `<i class="${selected.symbol}"></i>`;

  if (clientsToastTimer) {
    window.clearTimeout(clientsToastTimer);
  }

  toast.classList.remove("hidden", "opacity-0");
  toast.classList.add("flex", "opacity-100");

  clientsToastTimer = window.setTimeout(() => {
    hideClientsToast();
  }, 4200);
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
  const confirmed = await window.showSystemConfirm?.({
    titleText: "Excluir cliente",
    messageText: "Deseja realmente excluir este cliente? Essa ação remove o registro da base.",
    confirmText: "Excluir cliente",
    cancelText: "Cancelar",
    tone: "danger",
  });
  if (!confirmed) return;

  const response = await fetch(`/api/v1/clients/${clientId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (response.ok) {
    showClientsToast("Cliente excluído com sucesso.");
    clientsTable?.ajax.reload(null, false);
  } else {
    showClientsToast("Não foi possível excluir o cliente.", "error");
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
        .then(callback)
        .catch((error) => {
          console.error("Clients DataTable error:", error);
          callback({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
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
          return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tones[data] || "bg-[#eef3ff] text-[#476be8]"}">${labels[data] || data}</span>`;
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
      showClientsToast(feedback.textContent, "error");
    } catch {
      feedback.textContent = "Não foi possível salvar o cliente.";
      showClientsToast("Não foi possível salvar o cliente.", "error");
    }
    return;
  }

  closeModal("client-modal");
  resetClientForm();
  showClientsToast(clientId ? "Cliente atualizado com sucesso." : "Cliente cadastrado com sucesso.");
  clientsTable?.ajax.reload(null, false);
}

function submitBatchImportForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("batch-import-feedback");
  const file = document.getElementById("batch-import-file")?.files?.[0];

  if (!file) {
    feedback.textContent = "Selecione um arquivo para preparar a importação.";
    showClientsToast("Selecione um arquivo para preparar a importação.", "error");
    return;
  }

  feedback.textContent = "A interface de importação em lote está pronta. A integração do backend será conectada na próxima etapa.";
  closeModal("batch-import-modal");
  showClientsToast("Arquivo de importação recebido com sucesso. A integração em lote será conectada na próxima etapa.");
}

attachClientDocumentMask();
document.getElementById("client-form")?.addEventListener("submit", submitClientForm);
document.getElementById("batch-import-form")?.addEventListener("submit", submitBatchImportForm);
document.getElementById("open-client-modal")?.addEventListener("click", () => {
  resetClientForm();
  openModal("client-modal");
});
document.getElementById("open-batch-modal")?.addEventListener("click", () => {
  document.getElementById("batch-import-feedback").textContent = "";
  document.getElementById("batch-import-form")?.reset();
  openModal("batch-import-modal");
});
document.getElementById("clients-toast-close")?.addEventListener("click", hideClientsToast);
document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => closeModal(button.getAttribute("data-close-modal")));
});
if (window.jQuery && $("#clients-table").length) {
  initClientsTable();
}

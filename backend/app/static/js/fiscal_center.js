let documentsTable = null;
let lastManualAction = "processed";

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

function documentTypeLabel(type) {
  return type === "nfe" ? "nota fiscal" : "recibo";
}

async function loadClientsOptions() {
  const response = await fetch("/api/v1/clients", {
    headers: authHeaders({ Accept: "application/json" }),
  });

  if (!response.ok) return;

  const clients = await response.json();
  const selects = [document.getElementById("manual-client-id"), document.getElementById("auto-client-id")];

  selects.forEach((select) => {
    if (!select) return;
    const current = select.value;
    select.innerHTML = '<option value="">Selecione um cliente</option>';
    clients.forEach((client) => {
      const option = document.createElement("option");
      option.value = client.id;
      option.textContent = client.name;
      select.appendChild(option);
    });
    if (current) select.value = current;
  });
}

function resetManualForm() {
  lastManualAction = "processed";
  document.getElementById("manual-document-form")?.reset();
  document.getElementById("manual-document-id").value = "";
  document.getElementById("manual-status-wrap").classList.add("hidden");
  document.getElementById("manual-status").value = "processed";
  document.getElementById("manual-form-feedback").textContent = "";
}

function setManualFields(type, mode = "create") {
  const title = document.getElementById("manual-modal-title");
  const extra = document.getElementById("manual-extra-fields");
  const documentType = document.getElementById("manual-document-type");
  const statusWrap = document.getElementById("manual-status-wrap");
  const processButton = document.getElementById("manual-process-button");
  const draftButton = document.getElementById("manual-draft-button");

  if (!title || !extra || !documentType) return;

  documentType.value = type;
  title.textContent = mode === "edit" ? `Editar ${documentTypeLabel(type)}` : `Novo ${documentTypeLabel(type)} manual`;
  statusWrap.classList.toggle("hidden", mode !== "edit");
  processButton.textContent = mode === "edit" ? "Salvar alterações" : "Processar manualmente";
  draftButton.classList.toggle("hidden", mode === "edit");

  if (type === "receipt") {
    extra.innerHTML = `
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Recebedor</span>
        <input id="manual-receiver-name" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Nome do recebedor" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Documento do recebedor</span>
        <input id="manual-receiver-document" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="CPF/CNPJ" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Pagador</span>
        <input id="manual-payer-name" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Nome do pagador" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Documento do pagador</span>
        <input id="manual-payer-document" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="CPF/CNPJ" />
      </label>
      <label class="block md:col-span-2">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Forma de pagamento</span>
        <input id="manual-payment-method" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="PIX, TED, cartão..." />
      </label>
    `;
  } else {
    extra.innerHTML = `
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Emitente</span>
        <input id="manual-issuer-name" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Razão social / emitente" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Documento do emitente</span>
        <input id="manual-issuer-document" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="CNPJ" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Destinatário</span>
        <input id="manual-recipient-name" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Nome do destinatário" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Documento do destinatário</span>
        <input id="manual-recipient-document" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="CNPJ/CPF" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Série</span>
        <input id="manual-series" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Série da nota" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Chave de acesso</span>
        <input id="manual-access-key" class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Chave da NFe" />
      </label>
    `;
  }
}

function getManualPayload() {
  const documentType = document.getElementById("manual-document-type").value;
  const basePayload = {
    client_id: Number(document.getElementById("manual-client-id").value),
    document_type: documentType,
    action: lastManualAction,
    number: document.getElementById("manual-number").value.trim(),
    issue_date: document.getElementById("manual-issue-date").value,
    amount: Number(document.getElementById("manual-amount").value || 0),
    description: document.getElementById("manual-description").value.trim(),
  };

  if (documentType === "receipt") {
    return {
      ...basePayload,
      receiver_name: document.getElementById("manual-receiver-name")?.value.trim() || "",
      receiver_document: document.getElementById("manual-receiver-document")?.value.trim() || "",
      payer_name: document.getElementById("manual-payer-name")?.value.trim() || "",
      payer_document: document.getElementById("manual-payer-document")?.value.trim() || "",
      payment_method: document.getElementById("manual-payment-method")?.value.trim() || "",
    };
  }

  return {
    ...basePayload,
    issuer_name: document.getElementById("manual-issuer-name")?.value.trim() || "",
    issuer_document: document.getElementById("manual-issuer-document")?.value.trim() || "",
    recipient_name: document.getElementById("manual-recipient-name")?.value.trim() || "",
    recipient_document: document.getElementById("manual-recipient-document")?.value.trim() || "",
    series: document.getElementById("manual-series")?.value.trim() || "",
    access_key: document.getElementById("manual-access-key")?.value.trim() || "",
  };
}

function fillManualForm(data) {
  document.getElementById("manual-document-id").value = data.id;
  document.getElementById("manual-client-id").value = data.client_id;
  document.getElementById("manual-number").value = data.number || "";
  document.getElementById("manual-issue-date").value = data.issue_date || "";
  document.getElementById("manual-amount").value = data.amount || "";
  document.getElementById("manual-description").value = data.description || "";
  document.getElementById("manual-status").value = data.status || "processed";

  if (data.document_type === "receipt") {
    document.getElementById("manual-receiver-name").value = data.receiver_name || "";
    document.getElementById("manual-receiver-document").value = data.receiver_document || "";
    document.getElementById("manual-payer-name").value = data.payer_name || "";
    document.getElementById("manual-payer-document").value = data.payer_document || "";
    document.getElementById("manual-payment-method").value = data.payment_method || "";
  } else {
    document.getElementById("manual-issuer-name").value = data.issuer_name || "";
    document.getElementById("manual-issuer-document").value = data.issuer_document || "";
    document.getElementById("manual-recipient-name").value = data.recipient_name || "";
    document.getElementById("manual-recipient-document").value = data.recipient_document || "";
    document.getElementById("manual-series").value = data.series || "";
    document.getElementById("manual-access-key").value = data.access_key || "";
  }
}

async function openEditDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}`, {
    headers: authHeaders({ Accept: "application/json" }),
  });
  if (!response.ok) return;

  const data = await response.json();
  resetManualForm();
  setManualFields(data.document_type, "edit");
  fillManualForm(data);
  openModal("manual-modal");
}

async function deleteDocument(documentId) {
  const confirmed = window.confirm("Deseja realmente excluir este documento?");
  if (!confirmed) return;

  const response = await fetch(`/api/v1/documents/${documentId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (response.ok) {
    documentsTable?.ajax.reload(null, false);
  }
}

function initDocumentsTable() {
  documentsTable = $("#documents-table").DataTable({
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

      fetch(`/api/v1/documents/datatable?${params.toString()}`, {
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
          console.error("Documents DataTable error:", error);
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
        data: "title",
        render: function (data, _, row) {
          const initial = (data || "D").charAt(0).toUpperCase();
          return `
            <div class="flex items-center gap-3 min-w-[220px]">
              <span class="flex h-12 w-12 items-center justify-center rounded-full bg-[#edf3ff] font-bold text-[#4f7af7]">${initial}</span>
              <div>
                <p class="font-semibold text-[#31415f]">${data || "Documento"}</p>
                <p class="mt-1 text-sm text-[#7a88a3]">${row.subtitle || "Sem referência"}</p>
              </div>
            </div>
          `;
        },
      },
      { data: "client" },
      { data: "type" },
      { data: "entry" },
      {
        data: "status",
        render: function (data, _, row) {
          const tones = {
            processed: "bg-[#e9fbf2] text-[#16a765]",
            pending: "bg-[#fff3ea] text-[#e07a24]",
            draft: "bg-[#eef3ff] text-[#476be8]",
            cancelled: "bg-[#f4f5f8] text-[#6b7280]",
          };
          return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tones[row.status_code] || "bg-[#eef3ff] text-[#3478f6]"}">${data}</span>`;
        },
      },
      { data: "updated_at" },
      {
        data: "id",
        orderable: false,
        searchable: false,
        render: function (data) {
          return `
            <div class="flex items-center gap-3 text-[#4f7af7]">
              <button class="document-edit-btn" data-document-id="${data}" title="Editar"><i class="fa-solid fa-pen"></i></button>
              <button class="document-delete-btn text-[#e07a24]" data-document-id="${data}" title="Excluir"><i class="fa-solid fa-trash"></i></button>
            </div>
          `;
        },
      },
    ],
    language: {
      search: "Buscar:",
      lengthMenu: "Mostrar _MENU_ registros",
      info: "Mostrando _START_ a _END_ de _TOTAL_ documentos",
      zeroRecords: "Nenhum documento encontrado",
      paginate: {
        first: "Primeira",
        last: "Ultima",
        next: "Proxima",
        previous: "Anterior",
      },
    },
  });

  $("#documents-table").on("click", ".document-edit-btn", function () {
    openEditDocument(this.dataset.documentId);
  });

  $("#documents-table").on("click", ".document-delete-btn", function () {
    deleteDocument(this.dataset.documentId);
  });
}

async function submitManualForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("manual-form-feedback");
  const documentId = document.getElementById("manual-document-id").value;
  const payload = getManualPayload();

  if (!payload.client_id) {
    feedback.textContent = "Selecione um cliente antes de salvar.";
    return;
  }

  feedback.textContent = "Salvando documento...";

  const isEditing = Boolean(documentId);
  const requestPayload = isEditing
    ? { ...payload, status: document.getElementById("manual-status").value }
    : payload;
  const response = await fetch(isEditing ? `/api/v1/documents/${documentId}` : "/api/v1/documents/manual", {
    method: isEditing ? "PUT" : "POST",
    headers: authHeaders(),
    body: JSON.stringify(requestPayload),
  });

  if (!response.ok) {
    feedback.textContent = "Não foi possível salvar o documento.";
    return;
  }

  feedback.textContent = "Documento salvo com sucesso.";
  closeModal("manual-modal");
  resetManualForm();
  documentsTable?.ajax.reload(null, false);
}

async function submitAutomaticForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("auto-form-feedback");
  const clientId = document.getElementById("auto-client-id").value;
  const file = document.getElementById("auto-file").files[0];

  if (!clientId || !file) {
    feedback.textContent = "Selecione um cliente e um arquivo para enviar.";
    return;
  }

  const formData = new FormData();
  formData.append("client_id", clientId);
  formData.append("expected_type", document.getElementById("auto-expected-type").value);
  formData.append("notes", document.getElementById("auto-notes").value.trim());
  formData.append("file", file);

  feedback.textContent = "Enviando documento para análise...";

  const response = await fetch("/api/v1/documents/automatic", {
    method: "POST",
    headers: {
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
    },
    body: formData,
  });

  if (!response.ok) {
    feedback.textContent = "Não foi possível enviar o documento.";
    return;
  }

  feedback.textContent = "Documento enviado. Ele ficará pendente até validação humana.";
  event.target.reset();
  closeModal("auto-modal");
  documentsTable?.ajax.reload(null, false);
}

document.querySelectorAll("[data-manual-type]").forEach((button) => {
  button.addEventListener("click", () => {
    resetManualForm();
    setManualFields(button.getAttribute("data-manual-type"), "create");
    openModal("manual-modal");
  });
});

document.getElementById("manual-process-button")?.addEventListener("click", () => {
  lastManualAction = "processed";
});

document.getElementById("manual-draft-button")?.addEventListener("click", () => {
  lastManualAction = "draft";
});

document.getElementById("open-auto-modal")?.addEventListener("click", () => {
  document.getElementById("auto-form-feedback").textContent = "";
  openModal("auto-modal");
});

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    closeModal(button.getAttribute("data-close-modal"));
  });
});

document.getElementById("manual-document-form")?.addEventListener("submit", submitManualForm);
document.getElementById("auto-document-form")?.addEventListener("submit", submitAutomaticForm);

window.addEventListener("load", async () => {
  await loadClientsOptions();
  if (window.jQuery && $("#documents-table").length) {
    initDocumentsTable();
  }
});

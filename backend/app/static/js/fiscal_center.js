const documentsMock = [
  {
    id: 1,
    title: "NF 000124",
    client: "Atlas Capital",
    type: "Nota fiscal",
    entry: "OCR",
    status: "Processado",
    updated_at: "15/03/2026",
  },
  {
    id: 2,
    title: "Recibo 000091",
    client: "Bluewave Logistica",
    type: "Recibo",
    entry: "Manual",
    status: "Rascunho",
    updated_at: "14/03/2026",
  },
  {
    id: 3,
    title: "NF 000125",
    client: "Solaris Energy",
    type: "Nota fiscal",
    entry: "OCR",
    status: "Validando",
    updated_at: "13/03/2026",
  },
  {
    id: 4,
    title: "Recibo 000092",
    client: "Nova Aurora Tech",
    type: "Recibo",
    entry: "Manual",
    status: "Processado",
    updated_at: "12/03/2026",
  },
];

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("hidden");
  if (modal) modal.classList.add("flex");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("hidden");
  if (modal) modal.classList.remove("flex");
}

function setManualFields(type) {
  const title = document.getElementById("manual-modal-title");
  const extra = document.getElementById("manual-extra-fields");
  if (!title || !extra) return;

  if (type === "receipt") {
    title.textContent = "Novo recibo manual";
    extra.innerHTML = `
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Recebedor</span>
        <input class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Nome do recebedor" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Forma de pagamento</span>
        <input class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="PIX, TED, cartão..." />
      </label>
    `;
  } else {
    title.textContent = "Nova nota fiscal manual";
    extra.innerHTML = `
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Emitente</span>
        <input class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Razão social / emitente" />
      </label>
      <label class="block">
        <span class="mb-2 block text-sm font-medium text-[#51607d]">Chave de acesso</span>
        <input class="w-full rounded-2xl border border-[#dce5f4] px-4 py-3" placeholder="Chave da NFe" />
      </label>
    `;
  }
}

function initDocumentsTable() {
  $("#documents-table").DataTable({
    data: documentsMock,
    pageLength: 10,
    searching: true,
    lengthChange: true,
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
          const initial = data.charAt(0).toUpperCase();
          return `
            <div class="flex items-center gap-3 min-w-[220px]">
              <span class="flex h-12 w-12 items-center justify-center rounded-full bg-[#edf3ff] font-bold text-[#4f7af7]">${initial}</span>
              <div>
                <p class="font-semibold text-[#31415f]">${data}</p>
                <p class="mt-1 text-sm text-[#7a88a3]">Registro #${row.id}</p>
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
        render: function (data) {
          const tones = {
            Processado: "bg-[#e9fbf2] text-[#16a765]",
            Rascunho: "bg-[#fff3ea] text-[#e07a24]",
            Validando: "bg-[#f1ebff] text-[#7a5af8]",
          };
          return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tones[data] || "bg-[#eef3ff] text-[#3478f6]"}">${data}</span>`;
        },
      },
      { data: "updated_at" },
      {
        data: "id",
        orderable: false,
        searchable: false,
        render: function () {
          return `<div class="flex items-center gap-3 text-[#4f7af7]"><button title="Editar"><i class="fa-solid fa-pen"></i></button><button title="Excluir"><i class="fa-solid fa-trash"></i></button><button title="Mais"><i class="fa-solid fa-ellipsis"></i></button></div>`;
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
}

document.querySelectorAll("[data-manual-type]").forEach((button) => {
  button.addEventListener("click", () => {
    setManualFields(button.getAttribute("data-manual-type"));
    openModal("manual-modal");
  });
});

document.getElementById("open-auto-modal")?.addEventListener("click", () => {
  openModal("auto-modal");
});

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    closeModal(button.getAttribute("data-close-modal"));
  });
});

if (window.jQuery && $("#documents-table").length) {
  initDocumentsTable();
}

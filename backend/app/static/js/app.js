function getToken() {
  return localStorage.getItem("access_token");
}

function authHeaders(extra = {}) {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

function clearSessionAndRedirect() {
  localStorage.removeItem("access_token");
  window.location.href = "/";
}

let currentUserState = null;

function openGlobalModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeGlobalModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}

function setUserIdentity(user) {
  const name = user?.full_name || user?.email || "Usuario";
  const email = user?.email || "Sem email";
  const initial = (name || "U").trim().charAt(0).toUpperCase();
  currentUserState = user || null;

  document.getElementById("topbar-user-name")?.replaceChildren(document.createTextNode(name));
  document.getElementById("topbar-user-email")?.replaceChildren(document.createTextNode(email));
  document.getElementById("dropdown-user-name")?.replaceChildren(document.createTextNode(name));
  document.getElementById("dropdown-user-email")?.replaceChildren(document.createTextNode(email));
  document.getElementById("topbar-user-avatar")?.replaceChildren(document.createTextNode(initial));
}

function fillProfileForm() {
  document.getElementById("profile-full-name").value = currentUserState?.full_name || "";
  document.getElementById("profile-email").value = currentUserState?.email || "";
  document.getElementById("profile-form-feedback").textContent = "";
}

function resetPasswordForm() {
  document.getElementById("password-form")?.reset();
  document.getElementById("password-form-feedback").textContent = "";
}

async function loadCurrentUser() {
  const token = getToken();
  if (!token) return;

  try {
    const response = await fetch("/api/v1/auth/me", {
      headers: authHeaders({ Accept: "application/json" }),
    });

    if (response.status === 401) {
      clearSessionAndRedirect();
      return;
    }

    if (!response.ok) return;

    const user = await response.json();
    setUserIdentity(user);
  } catch (error) {
    console.error("Falha ao carregar usuario atual:", error);
  }
}

function initTopbarMenu() {
  const button = document.getElementById("user-menu-button");
  const dropdown = document.getElementById("user-menu-dropdown");
  const logoutButton = document.getElementById("user-logout-button");
  const profileButton = document.getElementById("user-profile-button");
  const accountButton = document.getElementById("user-account-button");

  if (!button || !dropdown) return;

  const closeMenu = () => dropdown.classList.add("hidden");
  const toggleMenu = () => dropdown.classList.toggle("hidden");

  button.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleMenu();
  });

  document.addEventListener("click", (event) => {
    if (!dropdown.contains(event.target) && !button.contains(event.target)) {
      closeMenu();
    }
  });

  logoutButton?.addEventListener("click", clearSessionAndRedirect);

  profileButton?.addEventListener("click", () => {
    closeMenu();
    fillProfileForm();
    openGlobalModal("profile-modal");
  });

  accountButton?.addEventListener("click", () => {
    closeMenu();
    resetPasswordForm();
    openGlobalModal("account-modal");
  });
}

async function submitProfileForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("profile-form-feedback");
  const payload = {
    full_name: document.getElementById("profile-full-name").value.trim(),
    email: document.getElementById("profile-email").value.trim(),
  };

  if (!payload.full_name || !payload.email) {
    feedback.textContent = "Preencha nome e e-mail para continuar.";
    return;
  }

  feedback.textContent = "Salvando alterações...";

  const response = await fetch("/api/v1/auth/me/profile", {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    feedback.textContent = data?.detail || "Não foi possível atualizar suas informações.";
    return;
  }

  setUserIdentity(data);
  feedback.textContent = "Informações atualizadas com sucesso.";
  window.setTimeout(() => closeGlobalModal("profile-modal"), 700);
}

async function submitPasswordForm(event) {
  event.preventDefault();
  const feedback = document.getElementById("password-form-feedback");
  const currentPassword = document.getElementById("account-current-password").value.trim();
  const newPassword = document.getElementById("account-new-password").value.trim();
  const confirmPassword = document.getElementById("account-confirm-password").value.trim();

  if (!currentPassword || !newPassword || !confirmPassword) {
    feedback.textContent = "Preencha todos os campos de senha.";
    return;
  }

  if (newPassword !== confirmPassword) {
    feedback.textContent = "A confirmação da nova senha não confere.";
    return;
  }

  feedback.textContent = "Atualizando senha...";

  const response = await fetch("/api/v1/auth/me/password", {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    feedback.textContent = data?.detail || "Não foi possível atualizar a senha.";
    return;
  }

  feedback.textContent = data?.message || "Senha atualizada com sucesso.";
  window.setTimeout(() => closeGlobalModal("account-modal"), 700);
}

document.querySelectorAll("[data-close-global-modal]").forEach((button) => {
  button.addEventListener("click", () => closeGlobalModal(button.getAttribute("data-close-global-modal")));
});

document.getElementById("profile-form")?.addEventListener("submit", submitProfileForm);
document.getElementById("password-form")?.addEventListener("submit", submitPasswordForm);

initTopbarMenu();
loadCurrentUser();

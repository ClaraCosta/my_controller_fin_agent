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

function setUserIdentity(user) {
  const name = user?.full_name || user?.email || "Usuario";
  const email = user?.email || "Sem email";
  const initial = (name || "U").trim().charAt(0).toUpperCase();

  document.getElementById("topbar-user-name")?.replaceChildren(document.createTextNode(name));
  document.getElementById("topbar-user-email")?.replaceChildren(document.createTextNode(email));
  document.getElementById("dropdown-user-name")?.replaceChildren(document.createTextNode(name));
  document.getElementById("dropdown-user-email")?.replaceChildren(document.createTextNode(email));
  document.getElementById("topbar-user-avatar")?.replaceChildren(document.createTextNode(initial));
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

  const showPlaceholder = (title) => {
    closeMenu();
    window.alert(`${title} estara disponivel na proxima iteracao.`);
  };

  profileButton?.addEventListener("click", () => showPlaceholder("Minhas informacoes"));
  accountButton?.addEventListener("click", () => showPlaceholder("Minha conta"));
}

initTopbarMenu();
loadCurrentUser();

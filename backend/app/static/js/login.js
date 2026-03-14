document.getElementById("login-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = {
    email: form.get("email"),
    password: form.get("password"),
  };

  const feedback = document.getElementById("login-feedback");
  feedback.textContent = "Autenticando...";

  const response = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    feedback.textContent = "Falha no login.";
    return;
  }

  const data = await response.json();
  localStorage.setItem("access_token", data.access_token);
  window.location.href = "/dashboard";
});


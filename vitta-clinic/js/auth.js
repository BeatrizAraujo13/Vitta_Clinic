/* Login, sessão persistente e regras simples de acesso por perfil. */
(function () {
  const permissions = {
    Administrador: { dashboard: "read", pacientes: "write", medicos: "write", especialidades: "write", consultas: "write", prontuarios: "write", relatorios: "read" },
    Médico: { dashboard: "read", pacientes: "read", consultas: "read", prontuarios: "write", relatorios: "read" },
    Recepcionista: { dashboard: "read", pacientes: "write", medicos: "read", especialidades: "read", consultas: "write", relatorios: "read" }
  };
  const api = {
    current() { return window.VittaStorage.session(); },
    can(page, action) {
      const user = this.current();
      const permission = user && permissions[user.role] && permissions[user.role][page];
      return action === "read" ? Boolean(permission) : permission === "write";
    },
    logout() {
      window.VittaStorage.clearSession();
      window.location.href = window.location.pathname.includes("/pages/") ? "../index.html" : "index.html";
    }
  };
  window.VittaAuth = api;

  const form = document.getElementById("login-form");
  if (!form) return;
  if (api.current()) window.location.href = "pages/dashboard.html";
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const error = document.getElementById("login-error");
    const email = form.elements.email.value.trim().toLowerCase();
    const password = form.elements.password.value;
    const user = window.VittaStorage.all("users").find((entry) => entry.email.toLowerCase() === email && entry.password === password);
    if (!user) {
      error.textContent = "E-mail ou senha inválidos. Confira os dados e tente novamente.";
      form.elements.password.setAttribute("aria-invalid", "true");
      return;
    }
    window.VittaStorage.setSession(user);
    window.location.href = "pages/dashboard.html";
  });
  form.addEventListener("input", () => {
    const error = document.getElementById("login-error");
    error.textContent = "";
    form.elements.password.removeAttribute("aria-invalid");
  });
})();

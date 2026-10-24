/* Acesso, sessão persistente e regras simples de permissão por perfil. */
(function () {
  const permissions = {
    Administrador: { dashboard: "read", pacientes: "write", medicos: "write", especialidades: "write", consultas: "write", prontuarios: "write", relatorios: "read" },
    Médico: { dashboard: "read", pacientes: "read", medicos: "read", consultas: "read", prontuarios: "write" },
    Recepcionista: { dashboard: "read", pacientes: "write", medicos: "read", especialidades: "read", consultas: "write" }
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
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const error = document.getElementById("login-error");
    const email = form.elements.email.value.trim().toLowerCase();
    const password = form.elements.password.value;
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    try {
      await window.VittaStorage.login(email, password);
      window.location.href = "pages/dashboard.html";
    } catch (failure) {
      error.textContent = failure.message || "Não foi possível entrar. Confira os dados e tente novamente.";
      form.elements.password.setAttribute("aria-invalid", "true");
    } finally {
      submit.disabled = false;
    }
  });
  form.addEventListener("input", () => {
    const error = document.getElementById("login-error");
    error.textContent = "";
    form.elements.password.removeAttribute("aria-invalid");
  });
})();

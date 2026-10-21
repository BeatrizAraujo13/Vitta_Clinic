/* Inicializa o layout comum, navegação, perfil e proteção das páginas. */
(function () {
  const pages = [
    ["dashboard", "Dashboard", "◫"], ["pacientes", "Pacientes", "♡"], ["medicos", "Médicos", "✚"],
    ["especialidades", "Especialidades", "✳"], ["consultas", "Consultas", "▣"], ["prontuarios", "Prontuários", "▤"], ["relatorios", "Relatórios", "▥"]
  ];
  const titles = { dashboard: "Visão geral", pacientes: "Pacientes", medicos: "Médicos", consultas: "Consultas", prontuarios: "Prontuários eletrônicos", especialidades: "Especialidades", relatorios: "Relatórios" };
  const path = window.location.pathname.split("/").pop().replace(".html", "");
  const user = window.VittaAuth.current();
  if (!user) { window.location.href = "../index.html"; return; }
  if (!window.VittaAuth.can(path, "read")) { window.location.href = "dashboard.html"; return; }

  const root = document.getElementById("app-root");
  const nav = pages.filter(([id]) => window.VittaAuth.can(id, "read")).map(([id, label, icon]) =>
    `<a href="${id}.html" aria-label="${label}" class="${id === path ? "active" : ""}" ${id === path ? 'aria-current="page"' : ""}><span class="nav-icon" aria-hidden="true">${icon}</span><span>${label}</span></a>`).join("");
  root.innerHTML = `<div class="app-shell"><aside class="sidebar"><a class="sidebar-brand" href="dashboard.html" aria-label="Vitta Clinic"><img src="../assets/images/logo.svg" alt=""><span>Vitta Clinic</span></a><nav class="sidebar-nav" aria-label="Navegação principal">${nav}<a href="#" data-logout aria-label="Sair"><span class="nav-icon" aria-hidden="true">↪</span><span>Sair</span></a></nav><div class="sidebar-bottom">Cuidado que conecta<br>© Vitta Clinic</div></aside><div class="main-area"><header class="topbar"><div class="topbar-title">${titles[path] || "Vitta Clinic"}</div><div class="user-menu"><div class="user-avatar" aria-hidden="true">${window.Vitta.escape(user.name.charAt(0))}</div><div class="user-info"><strong>${window.Vitta.escape(user.name)}</strong><span>${window.Vitta.escape(user.role)}</span></div><button class="button button-secondary button-small" type="button" data-logout>Sair</button></div></header><main class="page-content" data-page-content></main></div></div>`;
  document.querySelectorAll("[data-logout]").forEach((button) => button.addEventListener("click", (event) => { event.preventDefault(); window.VittaAuth.logout(); }));
  const moduleName = "init" + path.charAt(0).toUpperCase() + path.slice(1);
  document.addEventListener("DOMContentLoaded", () => {
    if (window.VittaModules && typeof window.VittaModules[moduleName] === "function") window.VittaModules[moduleName]();
  });
  window.VittaPage = { path, user };
})();

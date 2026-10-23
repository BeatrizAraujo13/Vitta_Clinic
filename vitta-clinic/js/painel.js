/* Indicadores operacionais, agenda futura e gráfico mensal do painel. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initDashboard = function () {
    const root = document.querySelector("[data-page-content]");
    const today = window.Vitta.today();
    const appointments = window.VittaStorage.all("appointments");
    const future = appointments.filter((item) => item.date >= today && item.status === "Agendada")
      .filter((item) => !window.VittaPage.user.doctorId || item.doctorId === window.VittaPage.user.doctorId)
      .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time));
    const todayCount = appointments.filter((item) => item.date === today && item.status !== "Cancelada")
      .filter((item) => !window.VittaPage.user.doctorId || item.doctorId === window.VittaPage.user.doctorId).length;
    const weekDate = new Date(); weekDate.setDate(weekDate.getDate() + 7);
    const weekEnd = window.Vitta.chaveData(weekDate);
    const weekCount = appointments.filter((item) => item.date >= today && item.date <= weekEnd && item.status === "Agendada")
      .filter((item) => !window.VittaPage.user.doctorId || item.doctorId === window.VittaPage.user.doctorId).length;
    const doctors = window.VittaStorage.all("doctors");
    const months = [];
    for (let offset = 5; offset >= 0; offset--) {
      const date = new Date(); date.setDate(1); date.setMonth(date.getMonth() - offset);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      const count = appointments.filter((item) => item.date.slice(0, 7) === key)
        .filter((item) => !window.VittaPage.user.doctorId || item.doctorId === window.VittaPage.user.doctorId).length;
      months.push({ label: date.toLocaleDateString("pt-BR", { month: "short" }).replace(".", ""), count });
    }
    const maximum = Math.max(1, ...months.map((item) => item.count));
    root.innerHTML = `<div class="page-heading"><div><h1>Olá, ${window.Vitta.escaparHtml(window.VittaPage.user.name.split(" ")[0])} 👋</h1><p>Acompanhe os indicadores e a agenda da clínica.</p></div><span class="status-pill">${window.Vitta.escaparHtml(window.Vitta.today().split("-").reverse().join("/"))}</span></div>
      <section class="stat-grid" aria-label="Indicadores">
        <article class="stat-card"><div class="stat-card-top"><span>Consultas hoje</span><span class="stat-icon">▣</span></div><div class="stat-value">${todayCount}</div><div class="stat-foot">Agendadas para hoje</div></article>
        <article class="stat-card"><div class="stat-card-top"><span>Pacientes cadastrados</span><span class="stat-icon">♡</span></div><div class="stat-value">${window.VittaStorage.all("patients").length}</div><div class="stat-foot">Base de pacientes</div></article>
        <article class="stat-card"><div class="stat-card-top"><span>Médicos ativos</span><span class="stat-icon">✚</span></div><div class="stat-value">${doctors.length}</div><div class="stat-foot">Profissionais cadastrados</div></article>
        <article class="stat-card"><div class="stat-card-top"><span>Próximos 7 dias</span><span class="stat-icon">◷</span></div><div class="stat-value">${weekCount}</div><div class="stat-foot">Consultas agendadas</div></article>
      </section>
      <div class="dashboard-grid"><section class="chart-card"><div class="card-heading"><h2>Consultas por mês</h2><span class="muted">Últimos 6 meses</span></div><div class="card-body"><div class="chart-bars" role="img" aria-label="Gráfico de consultas nos últimos seis meses">${months.map((item) => `<div class="chart-column"><div class="chart-bar" style="height:${Math.max(4, item.count / maximum * 82)}%"><span>${item.count}</span></div><span>${window.Vitta.escaparHtml(item.label)}</span></div>`).join("")}</div></div></section>
      <section class="content-card"><div class="card-heading"><h2>Próximas consultas</h2><a class="muted" href="consultas.html">Ver agenda →</a></div><div class="card-body"><div class="appointment-list">${future.slice(0, 5).map((item) => { const names = window.Vitta.appointmentName(item); const doctor = window.VittaStorage.all("doctors").find((entry) => entry.id === item.doctorId); return `<div class="appointment-row"><div class="appointment-time">${window.Vitta.escaparHtml(item.time)}</div><div><strong>${window.Vitta.escaparHtml(names.patient)}</strong><small>${window.Vitta.escaparHtml(names.doctor)} · ${window.Vitta.date(item.date)}</small></div><span class="status-pill">${window.Vitta.escaparHtml(doctor ? (window.VittaStorage.all("specialties").find((entry) => entry.id === doctor.specialtyId) || {}).name || "" : "")}</span></div>`; }).join("") || '<div class="empty-state">Nenhuma consulta futura agendada.</div>'}</div></div></section></div>`;
  };
})();

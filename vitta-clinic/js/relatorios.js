/* Relatórios locais de consultas e pacientes, com saída preparada para impressão. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initRelatorios = function () {
    const root = document.querySelector("[data-page-content]");
    const date = new Date();
    const initialFrom = window.Vitta.dateKey(new Date(date.getFullYear(), date.getMonth(), 1));
    const initialTo = window.Vitta.today();
    root.innerHTML = `<div class="page-heading"><div><h1>Relatórios</h1><p>Visualize os dados operacionais e imprima o resultado.</p></div><button type="button" class="button button-secondary no-print" data-print>Imprimir relatório</button></div>
      <section class="content-card"><div class="card-body"><div class="inline-filters no-print">
        <div class="field"><label for="report-type">Tipo de relatório</label><select id="report-type"><option value="period">Consultas por período</option><option value="patients">Pacientes cadastrados</option><option value="doctor">Consultas por médico</option></select></div>
        <div class="field" data-filter-from><label for="date-from">Data inicial</label><input id="date-from" type="date" value="${initialFrom}"></div>
        <div class="field" data-filter-to><label for="date-to">Data final</label><input id="date-to" type="date" value="${initialTo}"></div>
        <div class="field" data-filter-doctor hidden><label for="doctor-filter">Médico</label><select id="doctor-filter"></select></div>
        <button class="button button-primary" type="button" data-generate>Gerar relatório</button>
      </div></div><div class="card-heading"><h2 data-report-title>Consultas por período</h2></div><div class="card-body"><p class="report-summary" data-report-summary></p><div class="table-wrap"><table class="data-table" data-report-table><thead></thead><tbody></tbody></table></div></div></section>`;
    const type = root.querySelector("#report-type");
    const doctorFilter = root.querySelector("#doctor-filter");
    doctorFilter.innerHTML = window.VittaStorage.all("doctors").map((item) => `<option value="${window.Vitta.escape(item.id)}">${window.Vitta.escape(item.name)}</option>`).join("");
    function updateFilters() {
      const patients = type.value === "patients";
      root.querySelector("[data-filter-from]").hidden = patients;
      root.querySelector("[data-filter-to]").hidden = patients;
      root.querySelector("[data-filter-doctor]").hidden = type.value !== "doctor";
      root.querySelector("[data-report-title]").textContent = type.value === "patients" ? "Pacientes cadastrados" : type.value === "doctor" ? "Consultas por médico" : "Consultas por período";
    }
    function generate() {
      let rows;
      let columns;
      let summary;
      if (type.value === "patients") {
        rows = window.VittaStorage.all("patients").slice().sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
        columns = [
          { label: "Paciente", key: "name" }, { label: "CPF", key: "cpf" },
          { label: "Data de nascimento", render: (row) => window.Vitta.date(row.birthDate) },
          { label: "Telefone", key: "phone" }, { label: "Convênio", key: "insurance" }
        ];
        summary = `${rows.length} paciente(s) cadastrado(s).`;
      } else {
        const from = root.querySelector("#date-from").value;
        const to = root.querySelector("#date-to").value;
        if (from && to && from > to) { window.Vitta.toast("A data inicial deve ser anterior à data final.", "error"); return; }
        const doctorId = type.value === "doctor" ? doctorFilter.value : "";
        rows = window.VittaStorage.all("appointments").filter((item) => (!from || item.date >= from) && (!to || item.date <= to) && (!doctorId || item.doctorId === doctorId))
          .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time)).map((item) => {
            const names = window.Vitta.appointmentName(item);
            const doctor = window.VittaStorage.all("doctors").find((entry) => entry.id === item.doctorId);
            const specialty = doctor && window.VittaStorage.all("specialties").find((entry) => entry.id === doctor.specialtyId);
            return { ...item, patientName: names.patient, doctorName: names.doctor, specialtyName: specialty ? specialty.name : "—" };
          });
        columns = [
          { label: "Data", render: (row) => window.Vitta.date(row.date) }, { label: "Hora", key: "time" },
          { label: "Paciente", key: "patientName" }, { label: "Médico", key: "doctorName" },
          { label: "Especialidade", key: "specialtyName" },
          { label: "Status", key: "status" }
        ];
        const period = from || to ? ` de ${from ? window.Vitta.date(from) : "—"} até ${to ? window.Vitta.date(to) : "—"}` : "";
        summary = `${rows.length} consulta(s)${period}${doctorId ? ` para ${doctorFilter.selectedOptions[0].textContent}` : ""}.`;
      }
      root.querySelector("[data-report-summary]").textContent = summary;
      const table = root.querySelector("[data-report-table]");
      table.querySelector("thead").innerHTML = `<tr>${columns.map((column) => `<th>${window.Vitta.escape(column.label)}</th>`).join("")}</tr>`;
      table.querySelector("tbody").innerHTML = rows.length ? rows.map((row) => `<tr>${columns.map((column) => `<td>${column.render ? column.render(row) : window.Vitta.escape(row[column.key])}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="${columns.length}"><div class="empty-state">Nenhum registro encontrado para os filtros selecionados.</div></td></tr>`;
    }
    type.addEventListener("change", updateFilters);
    root.querySelector("[data-generate]").addEventListener("click", generate);
    root.querySelector("[data-print]").addEventListener("click", () => window.print());
    updateFilters();
    generate();
  };
})();

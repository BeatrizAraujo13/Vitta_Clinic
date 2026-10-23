/* Agenda e operações de consultas com filtros de período e situação. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initConsultas = function () {
    const writable = window.VittaAuth.can("consultas", "write");
    let dateFilter = "";
    let statusFilter = "";
    const renderizar = () => {
      const card = window.Vitta.tableFrame({
        title: "Consultas",
        description: "Agende e acompanhe os atendimentos da clínica.",
        searchPlaceholder: "Buscar paciente ou médico...",
        button: writable ? '<button class="button button-primary" type="button" data-add>＋ Agendar consulta</button>' : ""
      });
      const filters = card.querySelector("[data-extra-filters]");
      filters.innerHTML = `<input type="date" aria-label="Filtrar por data" data-date-filter><select aria-label="Filtrar por status" data-status-filter><option value="">Todos os status</option><option>Agendada</option><option>Realizada</option><option>Cancelada</option></select>`;
      filters.querySelector("[data-date-filter]").value = dateFilter;
      filters.querySelector("[data-status-filter]").value = statusFilter;
      const atualizarPorFiltro = () => {
        dateFilter = filters.querySelector("[data-date-filter]").value;
        statusFilter = filters.querySelector("[data-status-filter]").value;
        renderizar();
      };
      filters.querySelector("[data-date-filter]").addEventListener("change", atualizarPorFiltro);
      filters.querySelector("[data-status-filter]").addEventListener("change", atualizarPorFiltro);
      const doctors = window.VittaStorage.all("doctors");
      const specialties = window.VittaStorage.all("specialties");
      const rows = window.VittaStorage.all("appointments")
        .filter((item) => !window.VittaPage.user.doctorId || item.doctorId === window.VittaPage.user.doctorId)
        .filter((item) => !dateFilter || item.date === dateFilter)
        .filter((item) => !statusFilter || item.status === statusFilter)
        .map((item) => {
          const names = window.Vitta.appointmentName(item);
          const doctor = doctors.find((entry) => entry.id === item.doctorId);
          const specialty = doctor && specialties.find((entry) => entry.id === doctor.specialtyId);
          return { ...item, patientName: names.patient, doctorName: names.doctor, specialtyName: specialty ? specialty.name : "—", searchText: `${names.patient} ${names.doctor} ${specialty ? specialty.name : ""}` };
        }).sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time));
      window.Vitta.table({
        container: card,
        columns: [
          { label: "Data e hora", renderizar: (row) => `<span class="table-primary">${window.Vitta.date(row.date)}</span><span class="table-secondary">${window.Vitta.escaparHtml(row.time)}</span>` },
          { label: "Paciente", renderizar: (row) => window.Vitta.escaparHtml(row.patientName) },
          { label: "Médico / especialidade", renderizar: (row) => `<span>${window.Vitta.escaparHtml(row.doctorName)}</span><span class="table-secondary">${window.Vitta.escaparHtml(row.specialtyName)}</span>` },
          { label: "Status", renderizar: (row) => `<span class="status-pill ${row.status === "Cancelada" ? "cancelled" : row.status === "Realizada" ? "done" : ""}">${window.Vitta.escaparHtml(row.status)}</span>` }
        ],
        rows,
        actions: writable ? (row) => `<button type="button" class="button button-secondary button-small" data-edit="${window.Vitta.escaparHtml(row.id)}">Editar</button><button type="button" class="button button-danger button-small" data-delete="${window.Vitta.escaparHtml(row.id)}">Excluir</button>` : null
      });
      if (writable) {
        document.querySelector("[data-add]").addEventListener("click", () => editarConsulta());
        card.querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => editarConsulta(window.VittaStorage.all("appointments").find((item) => item.id === button.dataset.edit))));
        card.querySelectorAll("[data-delete]").forEach((button) => button.addEventListener("click", () => {
          const item = window.VittaStorage.all("appointments").find((entry) => entry.id === button.dataset.delete);
          if (window.VittaStorage.all("records").some((record) => record.appointmentId === item.id)) { window.Vitta.toast("Esta consulta possui prontuário vinculado e não pode ser excluída.", "error"); return; }
          window.Vitta.confirm({ title: "Excluir consulta?", message: `Deseja excluir a consulta de ${window.Vitta.appointmentName(item).patient}?`, onConfirm: () => window.VittaStorage.remove("appointments", item.id).then(() => { window.Vitta.toast("Consulta excluída."); renderizar(); }) });
        }));
      }
    };
    function editarConsulta(appointment) {
      const patients = window.VittaStorage.all("patients");
      const doctors = window.VittaStorage.all("doctors");
      if (!patients.length || !doctors.length) { window.Vitta.toast("Cadastre ao menos um paciente e um médico antes de agendar.", "error"); return; }
      const doctor = doctors.find((item) => item.id === (appointment && appointment.doctorId));
      const specialty = doctor && window.VittaStorage.all("specialties").find((item) => item.id === doctor.specialtyId);
      window.Vitta.modal({
        title: appointment ? "Editar consulta" : "Agendar consulta",
        values: { ...(appointment || {}), specialtyName: specialty ? specialty.name : "" },
        fields: [
          { name: "patientId", label: "Paciente", type: "select", required: true, options: () => patients.map((item) => ({ value: item.id, label: item.name })) },
          { name: "doctorId", label: "Médico", type: "select", required: true, options: () => doctors.map((item) => ({ value: item.id, label: item.name })) },
          { name: "specialtyName", label: "Especialidade", readOnly: true },
          { name: "date", label: "Data", type: "date", required: true, min: appointment ? undefined : window.Vitta.today() },
          { name: "time", label: "Hora", type: "time", required: true },
          { name: "status", label: "Status", type: "select", required: true, options: ["Agendada", "Realizada", "Cancelada"].map((value) => ({ value, label: value })) },
          { name: "notes", label: "Observações", type: "textarea", full: true }
        ],
        onSubmit: (form) => {
          const selectedDoctor = doctors.find((item) => item.id === form.doctorId);
          const selectedSpecialty = selectedDoctor && window.VittaStorage.all("specialties").find((item) => item.id === selectedDoctor.specialtyId);
          const changedTime = !appointment || form.date !== appointment.date || form.time !== appointment.time;
          const appointmentDate = new Date(form.date + "T" + form.time);
          if (changedTime && appointmentDate < new Date()) { window.Vitta.toast("Não é possível agendar ou remarcar uma consulta no passado.", "error"); return false; }
          const duplicate = window.VittaStorage.all("appointments").some((item) => item.id !== (appointment && appointment.id) && item.doctorId === form.doctorId && item.date === form.date && item.time === form.time && item.status !== "Cancelada");
          if (duplicate) { window.Vitta.toast("Este médico já possui consulta nesse horário.", "error"); return false; }
          return window.VittaStorage.save("appointments", { ...(appointment || {}), ...form, specialtyId: selectedSpecialty ? selectedSpecialty.id : "", id: appointment ? appointment.id : window.Vitta.id("con") }).then(() => {
            window.Vitta.toast(appointment ? "Consulta atualizada." : "Consulta agendada.");
            renderizar();
          });
        }
      });
      const doctorSelect = document.getElementById("field-doctorId");
      const specialtyInput = document.getElementById("field-specialtyName");
      doctorSelect.addEventListener("change", () => {
        const selectedDoctor = doctors.find((item) => item.id === doctorSelect.value);
        const selectedSpecialty = selectedDoctor && window.VittaStorage.all("specialties").find((item) => item.id === selectedDoctor.specialtyId);
        specialtyInput.value = selectedSpecialty ? selectedSpecialty.name : "";
      });
    }
    renderizar();
  };
})();

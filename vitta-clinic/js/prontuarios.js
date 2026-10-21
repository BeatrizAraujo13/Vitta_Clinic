/* Histórico clínico em linha do tempo; escrita restrita a médicos e administradores. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initProntuarios = function () {
    const writable = window.VittaAuth.can("prontuarios", "write");
    let patientFilter = "";
    const render = () => {
      const card = window.Vitta.tableFrame({
        title: "Prontuários eletrônicos",
        description: "Histórico clínico organizado por paciente e consulta.",
        searchPlaceholder: "Buscar paciente ou diagnóstico...",
        button: writable ? '<button class="button button-primary" type="button" data-add>＋ Novo prontuário</button>' : ""
      });
      const patients = window.VittaStorage.all("patients");
      const filter = document.createElement("select");
      filter.setAttribute("aria-label", "Filtrar histórico por paciente");
      filter.innerHTML = `<option value="">Todos os pacientes</option>${patients.map((item) => `<option value="${window.Vitta.escape(item.id)}">${window.Vitta.escape(item.name)}</option>`).join("")}`;
      filter.value = patientFilter;
      card.querySelector("[data-extra-filters]").appendChild(filter);
      filter.addEventListener("change", () => { patientFilter = filter.value; render(); });
      const rows = window.VittaStorage.all("records")
        .filter((item) => !patientFilter || item.patientId === patientFilter)
        .sort((a, b) => b.date.localeCompare(a.date))
        .map((record) => {
          const patient = patients.find((item) => item.id === record.patientId);
          const doctor = window.VittaStorage.all("doctors").find((item) => item.id === record.doctorId);
          const appointment = window.VittaStorage.all("appointments").find((item) => item.id === record.appointmentId);
          return { ...record, patientName: patient ? patient.name : "Paciente removido", doctorName: doctor ? doctor.name : "Médico removido", appointmentDate: appointment ? window.Vitta.date(appointment.date) : "Consulta removida", searchText: `${patient ? patient.name : ""} ${record.diagnosis} ${record.complaint}` };
        });
      window.Vitta.table({
        container: card,
        columns: [
          { label: "Data", render: (row) => `<span class="table-primary">${window.Vitta.date(row.date)}</span>` },
          { label: "Paciente / consulta", render: (row) => `<span class="table-primary">${window.Vitta.escape(row.patientName)}</span><span class="table-secondary">Consulta: ${window.Vitta.escape(row.appointmentDate)}</span>` },
          { label: "Médico", render: (row) => window.Vitta.escape(row.doctorName) },
          { label: "Queixa / diagnóstico", render: (row) => `<span>${window.Vitta.escape(row.complaint)}</span><span class="table-secondary">${window.Vitta.escape(row.diagnosis)}</span>` },
          { label: "Prescrição", render: (row) => window.Vitta.escape(row.prescription || "—") }
        ],
        rows,
        actions: writable ? (row) => `<button type="button" class="button button-secondary button-small" data-edit="${window.Vitta.escape(row.id)}">Editar</button><button type="button" class="button button-danger button-small" data-delete="${window.Vitta.escape(row.id)}">Excluir</button>` : null,
        emptyText: "Nenhum prontuário registrado para este paciente."
      });
      if (writable) {
        document.querySelector("[data-add]").addEventListener("click", () => editRecord());
        card.querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => editRecord(window.VittaStorage.all("records").find((item) => item.id === button.dataset.edit))));
        card.querySelectorAll("[data-delete]").forEach((button) => button.addEventListener("click", () => {
          const record = window.VittaStorage.all("records").find((item) => item.id === button.dataset.delete);
          window.Vitta.confirm({ title: "Excluir prontuário?", message: "Deseja excluir este registro clínico? Esta ação não pode ser desfeita.", onConfirm: () => { window.VittaStorage.remove("records", record.id); window.Vitta.toast("Prontuário excluído."); render(); } });
        }));
      }
    };
    function editRecord(record) {
      const patients = window.VittaStorage.all("patients");
      const appointments = window.VittaStorage.all("appointments");
      const doctors = window.VittaStorage.all("doctors");
      if (!patients.length || !appointments.length) { window.Vitta.toast("Cadastre pacientes e consultas antes de criar um prontuário.", "error"); return; }
      const values = { ...(record || {}), doctorId: record ? record.doctorId : "" };
      window.Vitta.modal({
        title: record ? "Editar prontuário" : "Novo prontuário",
        values,
        fields: [
          { name: "patientId", label: "Paciente", type: "select", required: true, options: () => patients.map((item) => ({ value: item.id, label: item.name })), onChange: (input, form) => updateAppointments(input.value, form) },
          { name: "appointmentId", label: "Consulta", type: "select", required: true, options: () => appointments.filter((item) => !record || item.patientId === record.patientId).map((item) => ({ value: item.id, label: `${window.Vitta.date(item.date)} às ${item.time}` })), onChange: (input, form) => {
            const appointment = appointments.find((item) => item.id === input.value);
            if (appointment) form.elements.doctorId.value = appointment.doctorId;
          } },
          { name: "date", label: "Data do atendimento", type: "date", required: true, max: window.Vitta.today(), value: window.Vitta.today() },
          { name: "doctorId", label: "Médico responsável", type: "select", required: true, options: () => doctors.map((item) => ({ value: item.id, label: item.name })) },
          { name: "complaint", label: "Queixa principal", type: "textarea", required: true, full: true },
          { name: "diagnosis", label: "Diagnóstico", type: "textarea", required: true, full: true },
          { name: "prescription", label: "Prescrição", type: "textarea", full: true },
          { name: "notes", label: "Observações", type: "textarea", full: true }
        ],
        onSubmit: (form) => {
          const appointment = appointments.find((item) => item.id === form.appointmentId);
          if (!appointment || appointment.patientId !== form.patientId) { window.Vitta.toast("Selecione uma consulta vinculada ao paciente escolhido.", "error"); return false; }
          if (appointment.doctorId !== form.doctorId) { window.Vitta.toast("O médico responsável deve corresponder ao médico da consulta.", "error"); return false; }
          window.VittaStorage.save("records", { ...(record || {}), ...form, id: record ? record.id : window.Vitta.id("pront") });
          window.Vitta.toast(record ? "Prontuário atualizado." : "Prontuário criado.");
          render();
        }
      });
      function updateAppointments(patientId, form) {
        const select = form.elements.appointmentId;
        const previous = select.value;
        select.replaceChildren(new Option("Selecione", ""));
        appointments.filter((item) => item.patientId === patientId).forEach((item) => select.add(new Option(`${window.Vitta.date(item.date)} às ${item.time}`, item.id)));
        if (Array.from(select.options).some((item) => item.value === previous)) select.value = previous;
        const selected = appointments.find((item) => item.id === select.value);
        if (selected) form.elements.doctorId.value = selected.doctorId;
      }
    }
    render();
  };
})();

/* CRUD e filtro de profissionais por especialidade. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initMedicos = function () {
    const writable = window.VittaAuth.can("medicos", "write");
    let specialtyFilter = "";
    const render = () => {
      const card = window.Vitta.tableFrame({
        title: "Médicos",
        description: "Gerencie os profissionais e suas especialidades.",
        searchPlaceholder: "Buscar por nome ou CRM...",
        button: writable ? '<button class="button button-primary" type="button" data-add>＋ Novo médico</button>' : ""
      });
      const specialties = window.VittaStorage.all("specialties");
      const filter = document.createElement("select");
      filter.setAttribute("aria-label", "Filtrar por especialidade");
      filter.innerHTML = `<option value="">Todas especialidades</option>${specialties.map((item) => `<option value="${window.Vitta.escape(item.id)}">${window.Vitta.escape(item.name)}</option>`).join("")}`;
      filter.value = specialtyFilter;
      card.querySelector("[data-extra-filters]").appendChild(filter);
      filter.addEventListener("change", () => { specialtyFilter = filter.value; render(); });
      const rows = window.VittaStorage.all("doctors").filter((item) => !specialtyFilter || item.specialtyId === specialtyFilter).map((doctor) => {
        const specialty = specialties.find((item) => item.id === doctor.specialtyId);
        return { ...doctor, specialtyName: specialty ? specialty.name : "Sem especialidade", searchText: `${doctor.name} ${doctor.crm} ${doctor.email || ""} ${specialty ? specialty.name : ""}` };
      });
      window.Vitta.table({
        container: card,
        columns: [
          { label: "Médico", render: (row) => `<span class="table-primary">${window.Vitta.escape(row.name)}</span><span class="table-secondary">${window.Vitta.escape(row.crm)}</span>` },
          { label: "Especialidade", render: (row) => window.Vitta.escape(row.specialtyName) },
          { label: "Contato", render: (row) => `<span>${window.Vitta.escape(row.email || "—")}</span><span class="table-secondary">${window.Vitta.escape(row.phone || "")}</span>` },
          { label: "Atendimento", render: (row) => window.Vitta.escape(row.schedule || "—") }
        ],
        rows,
        actions: writable ? (row) => `<button type="button" class="button button-secondary button-small" data-edit="${window.Vitta.escape(row.id)}">Editar</button><button type="button" class="button button-danger button-small" data-delete="${window.Vitta.escape(row.id)}">Excluir</button>` : null
      });
      if (writable) {
        document.querySelector("[data-add]").addEventListener("click", () => editDoctor());
        card.querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => editDoctor(window.VittaStorage.all("doctors").find((item) => item.id === button.dataset.edit))));
        card.querySelectorAll("[data-delete]").forEach((button) => button.addEventListener("click", () => {
          const doctor = window.VittaStorage.all("doctors").find((item) => item.id === button.dataset.delete);
          const linked = window.VittaStorage.all("appointments").some((item) => item.doctorId === doctor.id) || window.VittaStorage.all("records").some((item) => item.doctorId === doctor.id);
          if (linked) { window.Vitta.toast("Não é possível excluir: há consultas ou prontuários vinculados.", "error"); return; }
          window.Vitta.confirm({ title: "Excluir médico?", message: `Deseja excluir ${doctor.name}?`, onConfirm: () => { window.VittaStorage.remove("doctors", doctor.id); window.Vitta.toast("Médico excluído."); render(); } });
        }));
      }
    };
    function editDoctor(doctor) {
      if (!window.VittaStorage.all("specialties").length) { window.Vitta.toast("Cadastre uma especialidade antes de incluir médicos.", "error"); return; }
      window.Vitta.modal({
        title: doctor ? "Editar médico" : "Novo médico", values: doctor,
        fields: [
          { name: "name", label: "Nome completo", required: true, full: true },
          { name: "crm", label: "CRM", required: true },
          { name: "specialtyId", label: "Especialidade", type: "select", required: true, options: () => window.VittaStorage.all("specialties").map((item) => ({ value: item.id, label: item.name })) },
          { name: "email", label: "E-mail", type: "email" },
          { name: "phone", label: "Telefone", required: true },
          { name: "schedule", label: "Horário de atendimento", placeholder: "Ex.: Seg a sex, 08:00–17:00", full: true }
        ],
        onSubmit: (form) => {
          const duplicate = window.VittaStorage.all("doctors").some((item) => item.crm.toLowerCase() === form.crm.trim().toLowerCase() && item.id !== (doctor && doctor.id));
          if (duplicate) { window.Vitta.toast("Já existe um médico cadastrado com este CRM.", "error"); return false; }
          window.VittaStorage.save("doctors", { ...(doctor || {}), ...form, name: form.name.trim(), crm: form.crm.trim(), id: doctor ? doctor.id : window.Vitta.id("med") });
          window.Vitta.toast(doctor ? "Cadastro atualizado." : "Médico cadastrado.");
          render();
        }
      });
    }
    render();
  };
})();

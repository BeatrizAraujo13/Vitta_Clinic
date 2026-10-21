/* CRUD de pacientes com busca, validação de CPF e prevenção de duplicidades. */
(function () {
  window.VittaModules = window.VittaModules || {};
  window.VittaModules.initPacientes = function () {
    const writable = window.VittaAuth.can("pacientes", "write");
    const render = () => {
      const card = window.Vitta.tableFrame({
        title: "Pacientes",
        description: "Consulte e mantenha os dados dos pacientes da clínica.",
        searchPlaceholder: "Buscar por nome ou CPF...",
        button: writable ? '<button class="button button-primary" type="button" data-add>＋ Novo paciente</button>' : ""
      });
      const rows = window.VittaStorage.all("patients").map((patient) => ({
        ...patient,
        searchText: `${patient.name} ${patient.cpf} ${patient.email || ""}`
      }));
      window.Vitta.table({
        container: card,
        columns: [
          { label: "Paciente", render: (row) => `<span class="table-primary">${window.Vitta.escape(row.name)}</span><span class="table-secondary">${window.Vitta.escape(row.email || "Sem e-mail")}</span>` },
          { label: "CPF", render: (row) => window.Vitta.escape(row.cpf) },
          { label: "Telefone", render: (row) => window.Vitta.escape(row.phone || "—") },
          { label: "Convênio", render: (row) => window.Vitta.escape(row.insurance || "—") }
        ],
        rows,
        actions: writable ? (row) => `<button type="button" class="button button-secondary button-small" data-edit="${window.Vitta.escape(row.id)}">Editar</button><button type="button" class="button button-danger button-small" data-delete="${window.Vitta.escape(row.id)}">Excluir</button>` : null
      });
      if (writable) {
        document.querySelector("[data-add]").addEventListener("click", () => editPatient());
        card.querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => editPatient(window.VittaStorage.all("patients").find((item) => item.id === button.dataset.edit))));
        card.querySelectorAll("[data-delete]").forEach((button) => button.addEventListener("click", () => {
          const patient = window.VittaStorage.all("patients").find((item) => item.id === button.dataset.delete);
          const linked = window.VittaStorage.all("appointments").some((item) => item.patientId === patient.id) || window.VittaStorage.all("records").some((item) => item.patientId === patient.id);
          if (linked) {
            window.Vitta.confirm({ title: "Excluir paciente?", message: `O paciente ${patient.name} possui consultas ou prontuários vinculados. Excluir ainda assim poderá deixar esses registros sem vínculo.`, onConfirm: () => removePatient(patient.id) });
          } else window.Vitta.confirm({ title: "Excluir paciente?", message: `Deseja excluir ${patient.name}? Esta ação não pode ser desfeita.`, onConfirm: () => removePatient(patient.id) });
        }));
      }
    };
    function removePatient(id) {
      window.VittaStorage.remove("patients", id);
      window.Vitta.toast("Paciente excluído com sucesso.");
      render();
    }
    function editPatient(patient) {
      const editing = Boolean(patient);
      window.Vitta.modal({
        title: editing ? "Editar paciente" : "Novo paciente",
        values: patient,
        fields: [
          { name: "name", label: "Nome completo", required: true, full: true },
          { name: "cpf", label: "CPF", required: true, placeholder: "000.000.000-00", maxLength: 14 },
          { name: "birthDate", label: "Data de nascimento", type: "date", max: window.Vitta.today(), required: true },
          { name: "phone", label: "Telefone", required: true, placeholder: "(00) 00000-0000" },
          { name: "email", label: "E-mail", type: "email" },
          { name: "insurance", label: "Convênio" },
          { name: "address", label: "Endereço", full: true },
          { name: "notes", label: "Observações", type: "textarea", full: true }
        ],
        onSubmit: (form) => {
          const cpf = window.Vitta.cpfFormat(form.cpf);
          const duplicate = window.VittaStorage.all("patients").some((item) => item.cpf.replace(/\D/g, "") === cpf.replace(/\D/g, "") && item.id !== (patient && patient.id));
          if (duplicate) { window.Vitta.toast("Já existe um paciente cadastrado com este CPF.", "error"); return false; }
          const birth = new Date(form.birthDate + "T00:00:00");
          if (birth > new Date(window.Vitta.today() + "T23:59:59")) { window.Vitta.toast("A data de nascimento não pode estar no futuro.", "error"); return false; }
          window.VittaStorage.save("patients", { ...(patient || {}), ...form, cpf, id: patient ? patient.id : window.Vitta.id("pac") });
          window.Vitta.toast(editing ? "Cadastro atualizado." : "Paciente cadastrado.");
          render();
        }
      });
      const cpfInput = document.getElementById("field-cpf");
      cpfInput.addEventListener("input", () => { cpfInput.value = window.Vitta.cpfFormat(cpfInput.value); });
    }
    render();
  };
})();

/* Dados fictícios usados na primeira execução da demonstração. */
(function () {
  const dateKey = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
  const day = (offset) => {
    const date = new Date();
    date.setDate(date.getDate() + offset);
    return dateKey(date);
  };
  window.VittaSeed = {
    create: () => ({
      users: [
        { id: "user-admin", name: "Marina Costa", email: "admin@vitta.com", password: "123456", role: "Administrador" },
        { id: "user-doctor", name: "Dr. Rafael Mendes", email: "medico@vitta.com", password: "123456", role: "Médico", doctorId: "doc-1" },
        { id: "user-reception", name: "Camila Rocha", email: "recepcao@vitta.com", password: "123456", role: "Recepcionista" }
      ],
      specialties: [
        { id: "esp-1", name: "Cardiologia", description: "Prevenção, diagnóstico e tratamento das doenças do coração." },
        { id: "esp-2", name: "Dermatologia", description: "Cuidados clínicos com a pele, cabelos e unhas." },
        { id: "esp-3", name: "Clínica geral", description: "Atendimento integral e acompanhamento de saúde." }
      ],
      doctors: [
        { id: "doc-1", name: "Rafael Mendes", crm: "CRM-SP 123456", specialtyId: "esp-1", email: "rafael@vitta.com", phone: "(11) 98888-1200", schedule: "Seg a qui, 08:00–17:00" },
        { id: "doc-2", name: "Luciana Freitas", crm: "CRM-SP 234567", specialtyId: "esp-2", email: "luciana@vitta.com", phone: "(11) 97777-3400", schedule: "Seg a sex, 09:00–16:00" },
        { id: "doc-3", name: "André Oliveira", crm: "CRM-SP 345678", specialtyId: "esp-3", email: "andre@vitta.com", phone: "(11) 96666-5600", schedule: "Ter a sex, 08:00–18:00" }
      ],
      patients: [
        { id: "pac-1", name: "Ana Beatriz Lima", cpf: "529.982.247-25", birthDate: "1988-04-12", phone: "(11) 99911-2233", email: "ana.lima@email.com", address: "Rua das Flores, 120 — São Paulo/SP", insurance: "Vida Plena", notes: "" },
        { id: "pac-2", name: "Bruno Carvalho", cpf: "111.444.777-35", birthDate: "1976-11-03", phone: "(11) 99822-3344", email: "bruno.c@email.com", address: "Av. Central, 45 — São Paulo/SP", insurance: "Particular", notes: "" },
        { id: "pac-3", name: "Carolina Nunes", cpf: "123.456.789-09", birthDate: "1993-07-25", phone: "(11) 99733-4455", email: "carolina.n@email.com", address: "Rua Aurora, 88 — Guarulhos/SP", insurance: "Bem Saúde", notes: "Prefere contato por e-mail." },
        { id: "pac-4", name: "Diego Martins", cpf: "935.411.347-80", birthDate: "1982-02-14", phone: "(11) 99644-5566", email: "diego.m@email.com", address: "Alameda Sul, 310 — São Paulo/SP", insurance: "Vida Plena", notes: "" },
        { id: "pac-5", name: "Elisa Ferreira", cpf: "987.654.321-00", birthDate: "2001-09-08", phone: "(11) 99555-6677", email: "elisa.f@email.com", address: "Rua do Lago, 72 — Osasco/SP", insurance: "Bem Saúde", notes: "" }
      ],
      appointments: [
        { id: "con-1", patientId: "pac-1", doctorId: "doc-1", date: day(0), time: "09:00", status: "Agendada", notes: "Consulta de rotina." },
        { id: "con-2", patientId: "pac-2", doctorId: "doc-3", date: day(0), time: "10:30", status: "Agendada", notes: "" },
        { id: "con-3", patientId: "pac-3", doctorId: "doc-2", date: day(1), time: "14:00", status: "Agendada", notes: "" },
        { id: "con-4", patientId: "pac-4", doctorId: "doc-1", date: day(2), time: "11:00", status: "Agendada", notes: "" },
        { id: "con-5", patientId: "pac-5", doctorId: "doc-3", date: day(4), time: "08:30", status: "Agendada", notes: "Primeira consulta." }
      ],
      records: []
    })
  };
})();

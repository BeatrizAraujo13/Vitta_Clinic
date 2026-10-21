/* Persistência demonstrativa centralizada no localStorage do navegador. */
(function () {
  const DB_KEY = "vitta-clinic-db-v1";
  const SESSION_KEY = "vitta-clinic-session-v1";
  const collections = ["users", "patients", "doctors", "specialties", "appointments", "records"];
  const api = {
    read() {
      const raw = localStorage.getItem(DB_KEY);
      if (!raw) {
        const initial = window.VittaSeed.create();
        localStorage.setItem(DB_KEY, JSON.stringify(initial));
        return initial;
      }
      try {
        const data = JSON.parse(raw);
        collections.forEach((key) => { if (!Array.isArray(data[key])) data[key] = []; });
        return data;
      } catch (error) {
        console.error("Não foi possível ler os dados locais da Vitta Clinic.", error);
        throw new Error("Os dados locais estão inválidos. Limpe o armazenamento do site e tente novamente.");
      }
    },
    write(data) {
      localStorage.setItem(DB_KEY, JSON.stringify(data));
      window.dispatchEvent(new CustomEvent("vitta:data-changed"));
    },
    all(collection) {
      if (!collections.includes(collection)) throw new Error("Coleção desconhecida: " + collection);
      return this.read()[collection];
    },
    save(collection, item) {
      if (!collections.includes(collection)) throw new Error("Coleção desconhecida: " + collection);
      const data = this.read();
      const list = data[collection];
      const index = list.findIndex((entry) => entry.id === item.id);
      if (index < 0) list.unshift(item);
      else list[index] = item;
      this.write(data);
      return item;
    },
    remove(collection, id) {
      if (!collections.includes(collection)) throw new Error("Coleção desconhecida: " + collection);
      const data = this.read();
      data[collection] = data[collection].filter((entry) => entry.id !== id);
      this.write(data);
    },
    session() {
      try { return JSON.parse(localStorage.getItem(SESSION_KEY) || "null"); }
      catch (error) { console.error("Sessão local inválida.", error); return null; }
    },
    setSession(user) {
      const { id, name, email, role, doctorId } = user;
      localStorage.setItem(SESSION_KEY, JSON.stringify({ id, name, email, role, doctorId: doctorId || null }));
    },
    clearSession() { localStorage.removeItem(SESSION_KEY); },
    newId(prefix) {
      const value = window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
      return prefix + "-" + value;
    }
  };
  window.VittaStorage = api;
  api.read();
})();

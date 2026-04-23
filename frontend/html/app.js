const BACKEND_URL = "http://localhost:5000/api/team"; // ajusta si BACKEND_PORT != 5000

const statusEl = document.getElementById("backend-status");
const teamBody = document.getElementById("team-body");

function setStatus(ok, text) {
  statusEl.textContent = text;
  statusEl.className = `status ${ok ? "ok" : "error"}`;
}

function renderRows(members) {
  teamBody.innerHTML = "";
  members.forEach((m) => {
    const tr = document.createElement("tr");
    const estado = m.estado ?? "-";
    const badgeClass = String(estado).toLowerCase() === "activo" ? "badge badge--active" : "badge";
    tr.innerHTML = `
      <td>${m.nombre ?? "-"}</td>
      <td>${m.legajo ?? "-"}</td>
      <td>${m.feature ?? "-"}</td>
      <td>${m.servicio ?? "-"}</td>
      <td><span class="${badgeClass}">${estado}</span></td>
    `;
    teamBody.appendChild(tr);
  });
}

async function loadTeam() {
  try {
    const res = await fetch(BACKEND_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    // Soporta array directo o { integrantes: [...] }
    const members = Array.isArray(data) ? data : (data.integrantes ?? []);
    renderRows(members);
    setStatus(true, "Backend respondiendo correctamente");
  } catch (err) {
    setStatus(false, "Backend no responde");
    teamBody.innerHTML = "";
    console.error(err);
  }
}

loadTeam();
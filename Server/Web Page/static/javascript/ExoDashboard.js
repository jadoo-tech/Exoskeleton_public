const clientsListEl = document.getElementById("clientsList");
const emptyStateEl = document.getElementById("emptyState");
const connectedCountEl = document.getElementById("connectedCount");
const videoCountEl = document.getElementById("videoCount");
const lastRefreshEl = document.getElementById("lastRefresh");
const refreshBtn = document.getElementById("refreshBtn");

function openClientTab(clientId) {
    const url = `/exoDashboard/client/${encodeURIComponent(clientId)}`;
    window.open(url, "_blank", "noopener");
}

function formatAge(seconds) {
    if (!Number.isFinite(seconds)) {
        return "-";
    }
    if (seconds < 60) {
        return `${Math.floor(seconds)}s ago`;
    }
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
        return `${minutes}m ago`;
    }
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
}

function renderClients(clients) {
    clientsListEl.innerHTML = "";

    connectedCountEl.textContent = String(clients.length);
    videoCountEl.textContent = String(clients.filter((client) => client.video_connected).length);
    lastRefreshEl.textContent = new Date().toLocaleTimeString();

    if (!clients.length) {
        emptyStateEl.style.display = "block";
        return;
    }
    emptyStateEl.style.display = "none";

    const now = Date.now() / 1000;

    clients.forEach((client) => {
        const card = document.createElement("article");
        card.className = "client-card";
        card.addEventListener("click", () => openClientTab(client.client_id));

        const title = document.createElement("h3");
        title.className = "client-title";
        title.textContent = client.client_id;

        const session = document.createElement("p");
        session.className = "client-meta";
        session.textContent = `Session: ${client.session_id}`;

        const heartbeatAge = document.createElement("p");
        heartbeatAge.className = "client-meta";
        heartbeatAge.textContent = `Last heartbeat: ${formatAge(now - client.last_heartbeat)}`;

        const videoState = document.createElement("span");
        videoState.className = `status-pill ${client.video_connected ? "status-online" : "status-offline"}`;
        videoState.textContent = client.video_connected ? "Video Connected" : "Video Not Connected";

        card.appendChild(title);
        card.appendChild(session);
        card.appendChild(heartbeatAge);
        card.appendChild(videoState);
        clientsListEl.appendChild(card);
    });
}

async function refreshClients() {
    try {
        const response = await fetch("/clients");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const clients = await response.json();
        renderClients(Array.isArray(clients) ? clients : []);
    } catch (error) {
        console.error("Failed to load clients", error);
        emptyStateEl.textContent = "Failed to load clients.";
        emptyStateEl.style.display = "block";
    }
}

refreshBtn.addEventListener("click", refreshClients);
setInterval(refreshClients, 3000);
refreshClients();

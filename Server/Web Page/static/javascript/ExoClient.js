const clientId = window.EXO_CLIENT_ID;

const videoEl = document.getElementById("clientVideo");
const videoStateEl = document.getElementById("videoState");
const commandStatusEl = document.getElementById("commandStatus");
const historyBodyEl = document.getElementById("commandHistoryBody");

const startVideoBtn = document.getElementById("startVideoBtn");
const sendStepBtn = document.getElementById("sendStepBtn");
const sendDisplayBtn = document.getElementById("sendDisplayBtn");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

const stepInput = document.getElementById("stepInput");
const displayIndexInput = document.getElementById("displayIndexInput");
const displayTextInput = document.getElementById("displayTextInput");

function extractMsgId(message) {
    const match = message.match(/msg_id=([0-9a-f]+)/i);
    return match ? match[1] : null;
}

function formatTimestamp(secondsEpoch) {
    if (!Number.isFinite(secondsEpoch)) {
        return "-";
    }
    return new Date(secondsEpoch * 1000).toLocaleString();
}

function renderHistory(events) {
    historyBodyEl.innerHTML = "";

    if (!events.length) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 4;
        cell.textContent = "No commands sent for this client yet.";
        row.appendChild(cell);
        historyBodyEl.appendChild(row);
        return;
    }

    events.forEach((event) => {
        const row = document.createElement("tr");

        const timeCell = document.createElement("td");
        timeCell.textContent = formatTimestamp(event.sent_at);

        const commandCell = document.createElement("td");
        commandCell.textContent = event.command || "-";

        const ackCell = document.createElement("td");
        if (event.ack && typeof event.ack.accepted === "boolean") {
            ackCell.textContent = event.ack.accepted ? "Accepted" : "Rejected";
        } else {
            ackCell.textContent = "Pending";
        }

        const resultCell = document.createElement("td");
        if (event.result && event.result.status) {
            const detail = event.result.detail ? ` (${event.result.detail})` : "";
            resultCell.textContent = `${event.result.status}${detail}`;
        } else {
            resultCell.textContent = "Pending";
        }

        row.appendChild(timeCell);
        row.appendChild(commandCell);
        row.appendChild(ackCell);
        row.appendChild(resultCell);
        historyBodyEl.appendChild(row);
    });
}

async function refreshHistory() {
    try {
        const response = await fetch(`/commandHistory/${encodeURIComponent(clientId)}?limit=100`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const events = await response.json();
        renderHistory(Array.isArray(events) ? events : []);
    } catch (error) {
        console.error("Failed to load command history", error);
    }
}

async function pollCommandStatus(msgId) {
    for (let attempt = 0; attempt < 10; attempt += 1) {
        try {
            const response = await fetch(`/commandStatus/${msgId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const payload = await response.json();
            if (payload.result) {
                return payload;
            }
        } catch (error) {
            console.error("Failed polling command status", error);
            break;
        }
        await new Promise((resolve) => setTimeout(resolve, 250));
    }
    return null;
}

async function sendCommand(command) {
    const payload = `${command} on Client: ${clientId}`;
    commandStatusEl.textContent = `Sending: ${command}`;

    try {
        const response = await fetch("/commandClient", {
            method: "POST",
            headers: { "Content-Type": "text/plain" },
            body: payload,
        });
        const message = await response.text();
        commandStatusEl.textContent = message;

        const msgId = extractMsgId(message);
        if (msgId) {
            const status = await pollCommandStatus(msgId);
            if (status && status.result) {
                commandStatusEl.textContent = `${message} => ${status.result.status}`;
            }
        }

        refreshHistory();
    } catch (error) {
        console.error("Failed to send command", error);
        commandStatusEl.textContent = `Failed to send command: ${error}`;
    }
}

function refreshVideoSource() {
    const ts = Date.now();
    videoEl.src = `/video_feed/${encodeURIComponent(clientId)}?ts=${ts}`;
}

startVideoBtn.addEventListener("click", async () => {
    await sendCommand("start_video");
    refreshVideoSource();
});

sendStepBtn.addEventListener("click", async () => {
    const stepSize = Number.parseInt(stepInput.value, 10);
    if (!Number.isFinite(stepSize) || stepSize < 0) {
        commandStatusEl.textContent = "Step size must be a non-negative integer.";
        return;
    }
    await sendCommand(`step ${stepSize}`);
});

sendDisplayBtn.addEventListener("click", async () => {
    const displayIndex = Number.parseInt(displayIndexInput.value, 10);
    const displayText = displayTextInput.value.trim();

    if (!Number.isFinite(displayIndex) || displayIndex < 0) {
        commandStatusEl.textContent = "Display index must be a non-negative integer.";
        return;
    }
    if (!displayText) {
        commandStatusEl.textContent = "Display text cannot be empty.";
        return;
    }
    await sendCommand(`display ${displayIndex} ${displayText}`);
});

refreshHistoryBtn.addEventListener("click", refreshHistory);

videoEl.addEventListener("load", () => {
    videoStateEl.textContent = "Video stream connected.";
});

videoEl.addEventListener("error", () => {
    videoStateEl.textContent = "No stream yet. Click Start Video.";
});

setInterval(refreshHistory, 2500);
refreshHistory();

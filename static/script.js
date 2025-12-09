const API = {
    getPorts: () => fetch('/api/ports').then(r => r.json()),
    connect: (config) => fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    }).then(r => r.json()),
    disconnect: () => fetch('/api/disconnect', { method: 'POST' }).then(r => r.json()),
    send: (data) => fetch('/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(r => r.json()),
    readRegister: (data) => fetch('/api/read_register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(r => r.json())
};

// State
let isConnected = false;
let isScanning = false;

// UI Elements
const els = {
    portSelect: document.getElementById('portSelect'),
    refreshBtn: document.getElementById('refreshBtn'),
    connectBtn: document.getElementById('connectBtn'),
    status: document.getElementById('connectionStatus'),
    hexInput: document.getElementById('hexInput'),
    crcCheck: document.getElementById('crcCheck'),
    sendBtn: document.getElementById('sendBtn'),
    scanBtn: document.getElementById('scanBtn'),
    log: document.getElementById('logOutput'),
    clearLog: document.getElementById('clearLogBtn')
};

// Utils
const log = (msg, type = 'info') => {
    const div = document.createElement('div');
    div.className = `log-entry log-${type}`;
    div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    els.log.appendChild(div);
    els.log.scrollTop = els.log.scrollHeight;
};

// Handlers
async function refreshPorts() {
    try {
        const ports = await API.getPorts();
        els.portSelect.innerHTML = ports.map(p => `<option value="${p}">${p}</option>`).join('');
        if (ports.length === 0) {
            els.portSelect.innerHTML = '<option value="">No Ports Found</option>';
        }
    } catch (e) {
        log('Error fetching ports: ' + e, 'err');
    }
}

async function toggleConnection() {
    if (isConnected) {
        await API.disconnect();
        isConnected = false;
        els.connectBtn.textContent = 'Connect';
        els.status.textContent = 'Disconnected';
        els.status.classList.remove('connected');
        els.portSelect.disabled = false;
        log('Disconnected', 'info');
    } else {
        const port = els.portSelect.value;
        if (!port) return alert('Select a port');

        const config = {
            port: port,
            baudrate: document.getElementById('baudSelect').value,
            parity: document.getElementById('paritySelect').value
        };

        const res = await API.connect(config);
        if (res.error) {
            log('Connection failed: ' + res.error, 'err');
        } else {
            isConnected = true;
            els.connectBtn.textContent = 'Disconnect';
            els.status.textContent = 'Connected to ' + port;
            els.status.classList.add('connected');
            els.portSelect.disabled = true;
            log('Connected to ' + port, 'success');
        }
    }
}

async function sendCommand() {
    if (!isConnected) return alert('Not connected');

    const hex = els.hexInput.value;
    const useCrc = els.crcCheck.checked;

    log(`TX: ${hex} ${useCrc ? '(+CRC)' : ''}`, 'tx');

    const res = await API.send({ hex, use_crc: useCrc });
    if (res.error) {
        log('Error: ' + res.error, 'err');
    } else {
        if (res.tx) log(`Sent: ${res.tx}`, 'tx');
        if (res.rx) {
            log(`RX: ${res.rx} ${res.crc_valid ? '[CRC OK]' : '[CRC FAIL]'}`, 'rx');
        } else {
            log('RX: (No Response)', 'info');
        }
    }
}

async function startScan() {
    if (!isConnected) return alert('Not connected');
    if (isScanning) {
        isScanning = false;
        els.scanBtn.textContent = 'Start Scan';
        return;
    }

    isScanning = true;
    els.scanBtn.textContent = 'Stop Scan';
    log('--- Starting Scan ---', 'info');

    const slaveId = document.getElementById('scanId').value;
    const startAddr = parseInt(document.getElementById('scanStart').value);
    const count = parseInt(document.getElementById('scanCount').value);
    const funcCode = parseInt(document.getElementById('scanFunc').value);

    for (let i = 0; i < count; i++) {
        if (!isScanning) break;

        const addr = startAddr + i;
        const res = await API.readRegister({ slave_id: slaveId, address: addr, func_code: funcCode });

        if (res.status === 'ok') {
            log(`Reg ${addr}: ${res.value} (${res.hex})`, 'success');
        } else if (res.status === 'error') {
            log(`Reg ${addr}: Error (${res.message})`, 'err');
        } else if (res.status === 'no_response') {
            // Don't spam log for no response, maybe just every 10?
            // Or just log nothing to keep it clean, only log hits.
            // log(`Reg ${addr}: No Response`, 'info');
        } else if (res.error) {
            log(`Scan Error: ${res.error}`, 'err');
        }

        // Small delay to prevent UI freeze and bus saturation
        await new Promise(r => setTimeout(r, 50));
    }

    isScanning = false;
    els.scanBtn.textContent = 'Start Scan';
    log('--- Scan Complete ---', 'info');
}

// Init
els.refreshBtn.onclick = refreshPorts;
els.connectBtn.onclick = toggleConnection;
els.sendBtn.onclick = sendCommand;
els.scanBtn.onclick = startScan;
els.clearLog.onclick = () => els.log.innerHTML = '';

refreshPorts();

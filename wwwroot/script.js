document.addEventListener("DOMContentLoaded", () => {
    // Stores the latest full data package from the server
    let latestStats = null;
    // Toggles between 'circular' and 'bar' views
    let gaugeType = "circular";

    // Central object to hold references to key UI elements
    const ui = {
        mainView: document.getElementById("main-view"),
        historyView: document.getElementById("history-view"),
        status: document.getElementById("connection-status"),
        peakTemp: document.querySelector(".peak-temp"),
        buttons: {
            showHistory: document.getElementById("show-history-btn"),
            back: document.getElementById("back-btn"),
            refresh: document.getElementById("refresh-btn"),
            toggleGauge: document.getElementById("toggle-gauge-btn"),
        },
    };

    // --- Chart.js Setup ---
    const chartOptions = {
        scales: { y: { min: 0, max: 100, ticks: { color: "#d9e0ff" }, grid: { color: "rgba(136, 161, 255, 0.1)" } }, x: { ticks: { display: false }, grid: { color: "rgba(136, 161, 255, 0.1)" } } },
        plugins: { legend: { display: false } },
    };

    const createChart = (ctx, label, color) =>
        new Chart(ctx, {
            type: "line",
            data: { labels: Array(60).fill(""), datasets: [{ label, data: [], borderColor: color, backgroundColor: `${color}33`, borderWidth: 2, pointRadius: 0, tension: 0.4, fill: true }] },
            options: chartOptions,
        });

    const cpuChart = createChart(document.getElementById("cpuChart").getContext("2d"), "CPU", "#ff79c6");
    const gpuChart = createChart(document.getElementById("gpuChart").getContext("2d"), "GPU", "#bd93f9");

    /**
     * Updates a single dashboard widget with new data.
     * @param {HTMLElement} widget - The widget element to update.
     * @param {object} data - The full stats object from the server.
     */
    const updateWidget = (widget, data) => {
        const statName = widget.dataset.stat;
        const percentage = data[statName + "_load"];

        widget.querySelectorAll(".digital-readout").forEach((el) => {
            el.innerHTML = `${Math.round(percentage)}<span class="text-lg">%</span>`;
        });

        if (statName === "ram") {
            widget.querySelectorAll(".stat-usage").forEach((el) => {
                el.textContent = `${data.ram_used_gb.toFixed(1)}/${data.ram_total_gb.toFixed(1)} GB`;
            });
        } else {
            widget.querySelectorAll(".stat-temp").forEach((el) => {
                el.textContent = `${data[statName + "_temp"]}°C`;
            });
        }

        // Update both circular and bar progress visuals
        widget.querySelector(".gauge-arc-progress").style.strokeDasharray = `${percentage} 100`;
        widget.querySelector(".bar-fg").style.width = `${percentage}%`;
    };

    /**
     * Renders the historical data charts.
     */
    const renderGraphs = () => {
        if (!latestStats) return;
        cpuChart.data.datasets[0].data = latestStats.cpu_history;
        gpuChart.data.datasets[0].data = latestStats.gpu_history;
        cpuChart.update("none"); // 'none' prevents animation on refresh
        gpuChart.update("none");
    };

    /**
     * Toggles visibility between the main dashboard and the history view.
     * @param {string} viewToShow - The view to display ('main' or 'history').
     */
    const toggleView = (viewToShow) => {
        ui.mainView.classList.toggle("hidden", viewToShow === "history");
        ui.historyView.classList.toggle("hidden", viewToShow !== "history");
    };

    /**
     * Shows or hides gauge types (circular/bar) based on the current selection.
     */
    const updateGaugeDisplay = () => {
        document.querySelectorAll(".gauge-display").forEach((el) => el.classList.add("hidden"));
        document.querySelectorAll(`.gauge-display.${gaugeType}`).forEach((el) => el.classList.remove("hidden"));
        ui.buttons.toggleGauge.querySelector("span").textContent = gaugeType.charAt(0).toUpperCase() + gaugeType.slice(1);
    };

    // --- Event Listeners ---
    ui.buttons.showHistory.addEventListener("click", () => {
        toggleView("history");
        renderGraphs();
    });
    ui.buttons.back.addEventListener("click", () => toggleView("main"));
    ui.buttons.refresh.addEventListener("click", renderGraphs);
    ui.buttons.toggleGauge.addEventListener("click", () => {
        gaugeType = gaugeType === "circular" ? "bar" : "circular";
        updateGaugeDisplay();
    });

    // Set the initial gauge display on load
    updateGaugeDisplay();

    // --- WebSocket Connection ---
    // This dynamically constructs the WebSocket URL based on the page's current location.
    // It ensures the connection works whether accessed via localhost, IP address, or a domain.
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        ui.status.textContent = "ONLINE";
        ui.status.style.color = "#50fa7b";
    };

    ws.onclose = () => {
        ui.status.textContent = "OFFLINE";
        ui.status.style.color = "#ff5555";
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        latestStats = data; // Store the latest data for chart refreshes

        // Only update the main view if it's currently visible
        if (ui.mainView.classList.contains("hidden")) return;
        
        document.querySelectorAll(".dashboard-widget[data-stat]").forEach((w) => updateWidget(w, data));
        ui.peakTemp.innerHTML = `${Math.round(data.peak_temp)}<span class="text-3xl">°</span>`;
    };
});


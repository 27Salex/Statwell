# Statwell Monitor
A Real-Time PC Performance Dashboard
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/)


A sleek, modern, and real-time dashboard to monitor your PC's performance stats (CPU, GPU, RAM) through a web interface. Built with Python on the backend and a clean, responsive HTML/CSS/JS frontend.

This project is designed to be accessible from any device on your local network or via services like Tailscale, turning your phone, tablet, or another PC into a dedicated system monitor.

Demo of the dashboard interface:

## Table of Contents

- [✨ Features](#-features)
- [🛠️ Technology Stack](#-technology-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
- [⚙️ Usage](#-usage)
  - [Running the Server](#running-the-server)
  - [Stopping the Server](#stopping-the-server)
  - [Accessing the Dashboard](#-accessing-the-dashboard)
- [🤖 Automatic Startup on Windows](#-automatic-startup-on-windows)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Features

* **Real-Time Monitoring:** CPU, GPU, and RAM stats updated every second.
* **Integrated Web Server:** No external server needed. The Python script serves both the web page and the data via WebSockets.
* **Network Accessible:** View your dashboard from any device on your LAN or Tailscale network.
* **Dual View Modes:** Instantly switch between a "Circular" gauge and a "Bar" progress view.
* **Historical Analysis:** See beautiful charts of your CPU and GPU usage over the last 60 seconds.
* **NVIDIA GPU Support:** Uses the official `nvidia-ml-py` library for accurate load and temperature data from NVIDIA GPUs.
* **Configurable:** Easily change the host IP and port via the `config.ini` file.
* **Lightweight & Modern UI:** A futuristic, neon-themed dashboard that looks great on any screen.

---

## 🛠️ Technology Stack

* **Backend:** Python 3, `aiohttp` (Web Server), `websockets`, `psutil`, `nvidia-ml-py`
* **Frontend:** HTML5, CSS3 (with Tailwind CSS), JavaScript (vanilla)
* **Charting:** Chart.js

---

## 🚀 Getting Started

### Prerequisites

* Python 3.7+
* An NVIDIA GPU (recommended for accurate GPU stats). If you don't have one, the GPU stats will be simulated.

### Project Structure

Ensure your project files are organized as follows for the server to work correctly:

```
/PC-Monitor-Dashboard/
|-- backend.py
|-- config.ini
|-- start_monitor_startup.bat
|-- stop_monitor.bat
|-- /public/
    |-- index.html
    |-- style.css
    |-- script.js
```

### Installation

1.  Clone the repository (replace placeholders with your info):
    ```bash
    git clone [https://github.com/YOUR_USERNAME/PC-Monitor-Dashboard.git](https://github.com/YOUR_USERNAME/PC-Monitor-Dashboard.git)
    cd PC-Monitor-Dashboard
    ```
2.  Install the required Python libraries:
    ```bash
    pip install aiohttp psutil nvidia-ml-py
    ```

---

## ⚙️ Usage

### Running the Server

In a terminal, navigate to the project directory and run the backend script:
```bash
python backend.py
```
The server will start, and you'll see log messages confirming it's running on the configured host and port.

### Stopping the Server

To stop the server cleanly, simply double-click the `stop_monitor.bat` script. This will find the process by its port and terminate it.

### Accessing the Dashboard

* **On the host PC:** Open your browser and go to `http://localhost:8080` (or the port you set in `config.ini`).
* **From another device:** Find your host PC's local IP address (e.g., `192.168.1.100`) and go to `http://YOUR_LOCAL_IP:8080`.

---

## 🤖 Automatic Startup on Windows

To have the dashboard server start automatically when you log into Windows:

1.  **Open the Startup Folder:** Press `Windows Key + R`, type `shell:startup`, and press `Enter`.
2.  **Create a Shortcut:** In your project folder, right-click on **`start_monitor_startup.bat`** and select `Create shortcut`.
3.  **Move the Shortcut:** Drag and drop this new shortcut into the `shell:startup` folder.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

### How to Make a Pull Request

1.  **Fork the Project**
    Click the 'Fork' button at the top right of this page. This will create a copy of this repository in your own GitHub account.

2.  **Clone Your Fork** (replace YOUR_USERNAME)
    ```bash
    git clone [https://github.com/YOUR_USERNAME/PC-Monitor-Dashboard.git](https://github.com/YOUR_USERNAME/PC-Monitor-Dashboard.git)
    cd PC-Monitor-Dashboard
    ```

3.  **Create your Feature Branch**
    ```bash
    git checkout -b feature/AmazingFeature
    ```

4.  **Commit your Changes**
    Make your changes and commit them with a descriptive message.
    ```bash
    git commit -m 'Add some AmazingFeature'
    ```

5.  **Push to the Branch**
    ```bash
    git push origin feature/AmazingFeature
---

## 📜 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**.

[![CC BY-NC-SA 4.0](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

### This means you are free to:

* **Share** — copy and redistribute the material in any medium or format.
* **Adapt** — remix, transform, and build upon the material.

### Under the following terms:

* **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
* **NonCommercial** — You may not use the material for commercial purposes.
* **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

> **Full License Text:** You can find the full license details at [https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
        


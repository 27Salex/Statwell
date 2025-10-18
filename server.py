import asyncio
import json
import psutil
import logging
from collections import deque
import time
import configparser
from aiohttp import web
from pathlib import Path

# --- Get base path for the project ---
BASE_DIR = Path(__file__).parent
WWWROOT_DIR = BASE_DIR / 'wwwroot'

# --- NVIDIA Dependency ---
try:
    import pynvml
    NVIDIA_SUPPORT = True
except ImportError:
    NVIDIA_SUPPORT = False

# --- Configuration ---
config = configparser.ConfigParser()
config.read(BASE_DIR / 'config.ini')

HOST = config.get('server', 'host', fallback='0.0.0.0')
PORT = config.getint('server', 'port', fallback=80)
UPDATE_INTERVAL = 1  # Seconds between data updates
HISTORY_LENGTH = 60  # Number of data points to keep for charts
PEAK_TEMP_RESET_INTERVAL = 60  # Seconds to reset the peak temperature

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global State ---
connected_clients = set()
cpu_history = deque([0] * HISTORY_LENGTH, maxlen=HISTORY_LENGTH)
gpu_history = deque([0] * HISTORY_LENGTH, maxlen=HISTORY_LENGTH)
peak_temperature = 0
last_peak_temp_reset_time = time.time()
current_max_temp = 0

# --- Data Fetching Functions ---
def get_cpu_stats():
    """Gets the current CPU load and temperature."""
    cpu_load = psutil.cpu_percent(interval=None)
    try:
        temps = psutil.sensors_temperatures()
        # Prefer package temperature if available
        if 'coretemp' in temps:
            pkg_temps = [t.current for t in temps['coretemp'] if 'Package' in t.label]
            if pkg_temps:
                cpu_temp = pkg_temps[0]
            else:
                # Fallback to averaging all core temperatures
                cpu_temp = sum(t.current for t in temps['coretemp']) / len(temps['coretemp'])
        else:
            # Generic fallback if no specific sensor is found
            cpu_temp = 40.0 + (cpu_load * 0.4)
    except Exception:
        # Fallback if psutil fails to read sensors
        cpu_temp = 40.0 + (cpu_load * 0.4)
    return round(cpu_load, 1), round(cpu_temp, 1)

def get_ram_stats():
    """Gets the current RAM usage statistics."""
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024**3), mem.total / (1024**3)

def get_gpu_stats():
    """Gets GPU stats using pynvml for NVIDIA GPUs."""
    if NVIDIA_SUPPORT:
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_load = util.gpu
            gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            pynvml.nvmlShutdown()
            return round(float(gpu_load), 1), round(float(gpu_temp), 1)
        except Exception as e:
            logging.warning(f"Error reading NVIDIA data: {e}. Falling back to simulation.")
            return get_simulated_gpu_stats()
    else:
        return get_simulated_gpu_stats()

def get_simulated_gpu_stats():
    """Simulates GPU data if pynvml is not available."""
    cpu_load, _ = get_cpu_stats()
    # Simulate GPU load as being related to CPU load
    gpu_load = max(0, min(100, (cpu_load * 0.75) + 5))
    gpu_temp = 45.0 + (gpu_load * 0.35)
    return round(gpu_load, 1), round(gpu_temp, 1)

async def gather_stats():
    """Collects all system stats and packages them into a dictionary."""
    global peak_temperature, current_max_temp
    
    cpu_load, cpu_temp = get_cpu_stats()
    ram_load, ram_used_gb, ram_total_gb = get_ram_stats()
    gpu_load, gpu_temp = get_gpu_stats()

    # Update history deques
    cpu_history.append(cpu_load)
    gpu_history.append(gpu_load)
    
    # Update peak temperature logic
    current_max_temp = max(cpu_temp, gpu_temp)
    if current_max_temp > peak_temperature:
        peak_temperature = current_max_temp
        
    return {
        "cpu_load": cpu_load, "cpu_temp": cpu_temp, "cpu_history": list(cpu_history),
        "gpu_load": gpu_load, "gpu_temp": gpu_temp, "gpu_history": list(gpu_history),
        "ram_load": ram_load, "ram_used_gb": ram_used_gb, "ram_total_gb": ram_total_gb,
        "peak_temp": round(peak_temperature, 1),
    }

# --- Server Logic ---
async def reset_peak_temp_task():
    """A background task to reset the peak temperature periodically."""
    global peak_temperature, last_peak_temp_reset_time
    while True:
        await asyncio.sleep(1)
        if time.time() - last_peak_temp_reset_time > PEAK_TEMP_RESET_INTERVAL:
            peak_temperature = current_max_temp  # Reset to the current max, not zero
            last_peak_temp_reset_time = time.time()

async def websocket_handler(request):
    """Handles WebSocket connections."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.add(ws)
    logging.info(f"WebSocket client connected: {request.remote}")
    try:
        # Keep the connection open
        async for msg in ws:
            pass
    finally:
        connected_clients.remove(ws)
        logging.info(f"WebSocket client disconnected: {request.remote}")
    return ws

async def broadcast_stats():
    """Periodically gathers and sends stats to all connected clients."""
    while True:
        await asyncio.sleep(UPDATE_INTERVAL)
        if connected_clients:
            stats = await gather_stats()
            message = json.dumps(stats)
            # Use a copy of the set to avoid issues if a client disconnects during broadcast
            for ws in set(connected_clients):
                if not ws.closed:
                    await ws.send_str(message)

async def index_handler(request):
    """Serves the main index.html file."""
    return web.FileResponse(WWWROOT_DIR / 'index.html')

async def main():
    """Main function to set up and start the server."""
    if not WWWROOT_DIR.exists() or not WWWROOT_DIR.is_dir():
        logging.error(f"'wwwroot' folder not found at {WWWROOT_DIR}")
        logging.error("Please ensure the folder structure is correct.")
        return

    if NVIDIA_SUPPORT:
        logging.info("NVIDIA support (nvidia-ml-py) detected.")
    else:
        logging.warning("'nvidia-ml-py' library not found. GPU stats will be SIMULATED.")

    app = web.Application()
    
    # --- Route Setup ---
    app.router.add_get('/', index_handler)         # Route for the main page
    app.router.add_get('/ws', websocket_handler) # Route for the WebSocket connection
    app.router.add_static('/', path=WWWROOT_DIR, name='static') # Serves static files like css, js

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    
    logging.info(f"HTTP and WebSocket server started at http://{HOST}:{PORT}")
    logging.info("To access from your local network, use this PC's IP address.")
    
    # Start background tasks
    asyncio.create_task(broadcast_stats())
    asyncio.create_task(reset_peak_temp_task())
    
    await site.start()
    
    # Keep the server running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped.")


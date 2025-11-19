import argparse
import threading
import time
import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import serial

# Try to import BrainLinkParser
try:
    from BrainLinkParser import BrainLinkParser
except ImportError:
    sys.exit("Error: BrainLinkParser.so/.pyd not found. Make sure it is in the same directory.")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
latest_data: Dict[str, Any] = {
    "eeg": {
        "attention": 0,
        "meditation": 0,
        "delta": 0,
        "theta": 0,
        "lowAlpha": 0,
        "highAlpha": 0,
        "lowBeta": 0,
        "highBeta": 0,
        "lowGamma": 0,
        "highGamma": 0,
    },
    "extended": {
        "ap": 0,
        "battery": 0,
        "version": 0,
        "gnaw": 0,
        "temperature": 0,
        "heart": 0,
    },
    "gyro": {"x": 0, "y": 0, "z": 0},
    "rr": {"rr1": 0, "rr2": 0, "rr3": 0},
    "raw": 0,
    "connected": False
}

last_packet_time = 0

def update_eeg(data):
    global last_packet_time
    last_packet_time = time.time()
    latest_data["eeg"] = {
        "attention": data.attention,
        "meditation": data.meditation,
        "delta": data.delta,
        "theta": data.theta,
        "lowAlpha": data.lowAlpha,
        "highAlpha": data.highAlpha,
        "lowBeta": data.lowBeta,
        "highBeta": data.highBeta,
        "lowGamma": data.lowGamma,
        "highGamma": data.highGamma,
    }

def update_extended(data):
    global last_packet_time
    last_packet_time = time.time()
    latest_data["extended"] = {
        "ap": data.ap,
        "battery": data.battery,
        "version": data.version,
        "gnaw": data.gnaw,
        "temperature": data.temperature,
        "heart": data.heart,
    }

def update_gyro(x, y, z):
    global last_packet_time
    last_packet_time = time.time()
    latest_data["gyro"] = {"x": x, "y": y, "z": z}

def update_rr(rr1, rr2, rr3):
    global last_packet_time
    last_packet_time = time.time()
    latest_data["rr"] = {"rr1": rr1, "rr2": rr2, "rr3": rr3}

def update_raw(raw):
    global last_packet_time
    last_packet_time = time.time()
    latest_data["raw"] = raw

def serial_reader(port: str, baud: int):
    parser = BrainLinkParser(
        eeg_callback=update_eeg,
        extend_eeg_callback=update_extended,
        gyro_callback=update_gyro,
        rr_callback=update_rr,
        raw_callback=update_raw,
    )
    
    while True:
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                print(f"Connected to {port} @ {baud}")
                # Don't set connected=True here, wait for data
                while True:
                    chunk = ser.read(ser.in_waiting or 1)
                    if chunk:
                        parser.parse(chunk)
                    else:
                        time.sleep(0.01)
        except Exception as e:
            print(f"Serial error: {e}")
            time.sleep(2) # Wait before reconnecting

@app.get("/data")
def get_data():
    # Check if data is stale (e.g., > 2 seconds old)
    is_connected = (time.time() - last_packet_time) < 2.0
    latest_data["connected"] = is_connected
    return latest_data

def start_server(port: str, baud: int):
    # Start serial thread
    t = threading.Thread(target=serial_reader, args=(port, baud), daemon=True)
    t.start()
    
    # Start API server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BrainLink API Server")
    parser.add_argument("--port", required=True, help="Serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    args = parser.parse_args()
    
    start_server(args.port, args.baud)

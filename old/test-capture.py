#!/usr/bin/env python3
import subprocess
import time
import csv
import os
from datetime import datetime
import pyvisa

# ───────────────── CONFIGURATION ────────────────────────────────────────────
# Proxmark3 CLI device and command (adjust your tag/type as needed)
PM3_DEV   = "/dev/ttyACM0"
PM3_CMD = [
    "proxmark3",
    "-p", PM3_DEV,
    "-c", "hf search"
]

# Scope VISA string (USBTMC mode must be enabled on USB-B)
SCOPE_RES = "USB0::2733::470::100969::0::INSTR"

# How many points to fetch (must match your :ACQUIRE:POINTS)
POINTS    = 10000

# Where to drop CSVs
OUT_DIR   = os.path.expanduser("~/Desktop")

# ────────────────────────────────────────────────────────────────────────────

def trigger_proxmark():
    print("🔊 Triggering Proxmark3…")
    subprocess.run(PM3_CMD, check=True)
    print("✅ Proxmark sequence complete.")

def setup_scope(scope):
    print("⚙️  Configuring scope…")
    scope.write("*RST")
    scope.write(f":ACQUIRE:POINTS {POINTS}")
    scope.write(":CHAN1:DISP ON")
    scope.write(":CHAN1:SCAL 0.2")
    scope.write(":TIM:SCAL 20e-6")
    scope.write(":TRIG:MODE AUTO")
    scope.write(":TRIG:EDGE:SOUR CHAN1")
    scope.write(":TRIG:EDGE:SLOP POS")
    scope.write(":TRIG:LEV 0.01")

def capture_wave(scope):
    print("⏳ Arming single‐shot capture…")
    scope.write(":SINGLE")
    time.sleep(0.5)

    print("📥 Fetching waveform data…")
    scope.write(":WAVEFORM:FORMAT ASCII")
    scope.write(f":WAVEFORM:POINTS {POINTS}")
    data = scope.query_ascii_values(":WAVEFORM:DATA?")
    print(f"✅ Retrieved {len(data)} samples.")
    return data

def save_csv(data):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(OUT_DIR, f"wave_{ts}.csv")
    print(f"💾 Writing CSV → {fname}")
    with open(fname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Sample", "Voltage_V"])
        for i, v in enumerate(data):
            w.writerow([i, v])
    print("✅ CSV saved.")
    return fname

def main():
    # 1) Launch and locate the scope
    rm    = pyvisa.ResourceManager()
    scope = rm.open_resource(SCOPE_RES)
    scope.write_termination = "\n"
    scope.read_termination  = "\n"
    scope.timeout           = 10000

    print("Connected to:", scope.query("*IDN?").strip())

    # 2) Prep the scope once
    setup_scope(scope)

    # 3) Trigger Proxmark → Capture → Save
    trigger_proxmark()
    samples = capture_wave(scope)
    csv_file = save_csv(samples)

    scope.close()
    print("🎉 Done. File:", csv_file)

if __name__ == "__main__":
    main()

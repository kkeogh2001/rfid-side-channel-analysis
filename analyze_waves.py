#!/usr/bin/env python3
import glob, os
import pandas as pd
import matplotlib.pyplot as plt

# ── CONFIG ─────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser("~/Desktop/waves")
OUTPUT_MASTER = os.path.join(DATA_DIR, "all_waves.csv")
# ───────────────────────────────────────────────────────────────────────────

# 1) Gather and label each file
files = sorted(glob.glob(os.path.join(DATA_DIR, "wave_*.csv")))
if not files:
    raise SystemExit("❌ No wave_*.csv files found in " + DATA_DIR)

dfs = []
for idx, path in enumerate(files, start=1):
    df = pd.read_csv(path)
    df["Shot"] = idx
    dfs.append(df)

# 2) Concatenate all data
master = pd.concat(dfs, ignore_index=True)
master.to_csv(OUTPUT_MASTER, index=False)
print(f"✅ Master CSV written to {OUTPUT_MASTER}")

# 3) Plotting
plt.figure(figsize=(8, 5))
for idx, grp in master.groupby("Shot"):
    plt.plot(grp["Sample"], grp["Voltage_V"], label=f"Shot {idx}")

plt.xlabel("Sample Index")
plt.ylabel("Voltage (V)")
plt.title("Overlay of 10 Proxmark3 Waveform Captures")
plt.legend(loc="upper right", ncol=2, fontsize="small")
plt.grid(True)
plt.tight_layout()
plt.show()

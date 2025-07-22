import time
import csv
import subprocess
from datetime import datetime

master_csv = 'timing_metadata.csv'

print("Timing capture started. Press Enter to begin each trial.")
while True:
    label = input("Enter trace label (e.g. wave_01) or 'q' to quit: ").strip()
    if label.lower() == 'q':
        break

    input(f"→ Ready to start '{label}'. Press Enter to run Proxmark command and start timing...")

    t_start = time.perf_counter()
    start_ts = datetime.now().isoformat()

    # ✅ Run Proxmark3 Crypto1 command
    try:
        result = subprocess.run(
            ['bash', '-c', 'echo "hf mf chk --1k -a --tblk 0 -k 434A9734E087" | proxmark3 /dev/ttyACM0'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        print(result.stderr)
        t_end = time.perf_counter()
        end_ts = datetime.now().isoformat()
        duration = t_end - t_start
    except subprocess.TimeoutExpired:
        print("⚠️ Proxmark command timed out!")

    input("→ Press Enter once you've saved the waveform on the scope...")



    comment = input("Optional comment (e.g. command type): ").strip()

    with open(master_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([label, start_ts, end_ts, f"{duration:.6f}", comment])

    print(f"✅ Logged '{label}' — {duration:.2f} seconds\n")

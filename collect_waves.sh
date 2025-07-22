#!/usr/bin/env bash
set -euo pipefail

PM3_DEV="/dev/ttyACM0"
USBTMC="/dev/usbtmc0"
OUTDIR="$HOME/Desktop/waves"
TRIES=10
TERM=$'\n'

# helper to send SCPI and capture data
scpi_query() {
  printf "%s%s" "$1" "$TERM" > "$USBTMC"
  sleep 0.1
  cat "$USBTMC" | tr -d '\r'
}

mkdir -p "$OUTDIR"

for i in $(seq 1 $TRIES); do
  echo "=== Shot $i/$TRIES ==="

  # trigger Proxmark
  echo "hf search; exit" | proxmark3 -p "$PM3_DEV" -i

  # single‐shot the scope
  scpi_query "*RST"
  scpi_query ":ACQUIRE:POINTS 10000"
  scpi_query ":SINGLE"
  sleep 0.5

  # fetch waveform ASCII
  scpi_query ":WAVEFORM:FORMAT ASCII" > /dev/null
  scpi_query ":WAVEFORM:POINTS 10000" > /dev/null

  echo "Fetching data…"
  printf "%s%s" ":WAVEFORM:DATA?" "$TERM" > "$USBTMC"
  sleep 0.2

  # write to CSV
  OUT="$OUTDIR/wave_${i}.csv"
  { echo "Sample,Voltage_V"
    cat "$USBTMC" | tr -d '\r' \
      | awk -F, '{for(j=1;j<=NF;j++) print j","$j}'
  } > "$OUT"
  echo "Saved $OUT"
done

echo "All done. Files in $OUTDIR"

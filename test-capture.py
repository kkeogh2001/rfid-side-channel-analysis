from pyvisa import ResourceManager, VisaIOError
import time, csv, subprocess, re
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
import matplotlib.pyplot as plt

def wait_opc(dev):
    """Helper to wait for previous SCPI write to finish."""
    return dev.query('*OPC?')

# --- CONFIGURATION ---
BLOCK      = 8
KEY_TYPE   = 'B'
KEY        = 'FFFFFFFFFFFF'
PORT       = '/dev/ttyACM0'
AES_KEY    = b'Sixteen byte key'
PLAINTEXT  = b'Test12345678DATA'
CYCLES     = 3
POINTS     = 4096

# --- PREPARE ENCRYPTED PAYLOAD ---
cipher      = AES.new(AES_KEY, AES.MODE_ECB)
payload     = cipher.encrypt(PLAINTEXT)
hex_payload = hexlify(payload).upper().decode()
print(f"Plaintext : {PLAINTEXT!r}")
print(f"Encrypted : {hex_payload}\n")

results = []

# --- OPEN RESOURCE MANAGER & SCOPE (no 'with') ---
rm    = ResourceManager()
scope = rm.open_resource('USB0::2733::470::100969::0::INSTR')

# Configure VISA session
scope.read_termination  = '\n'
scope.write_termination = '\n'
scope.timeout    = 20000       # 20 s
scope.chunk_size = 512 * 1024  # 512 KiB

print("Connected to:", scope.query('*IDN?').strip(), "\n")

# Reset & STOP any running acquisition
scope.write('*RST');   wait_opc(scope)
scope.write(':STOP');  wait_opc(scope)
print("Scope reset & stopped\n")

# Trigger CH1 rising-edge
scope.write(':TRIGGER:MODE EDGE');          wait_opc(scope)
scope.write(':TRIGGER:EDGE:SOURCE CHAN1');  wait_opc(scope)
scope.write(':TRIGGER:EDGE:SLOPE POSITIVE');wait_opc(scope)
print("Trigger = CH1, rising-edge\n")

# Static memory depth + channel source
scope.write(':ACQUIRE:MEMDEPTH NORMAL'); wait_opc(scope)
scope.write(':WAVEFORM:SOURCE CHAN1');   wait_opc(scope)
print("Memory depth = NORMAL (~14 kpts), source = CH1\n")

# --- MAIN CYCLE LOOP ---
for cycle in range(1, CYCLES+1):
    print(f"=== Cycle {cycle} ===")

    # 1) Write encrypted block via Proxmark3
    subprocess.run([
        'proxmark3', PORT, '-c',
        f'hf mf wrbl --blk {BLOCK} -{KEY_TYPE.lower()} '
        f'-k {KEY} -d {hex_payload}'
    ], capture_output=True, text=True)
    time.sleep(0.2)

    # 2) Read & extract back
    rd = subprocess.run([
        'proxmark3', PORT, '-c',
        f'hf mf rdbl --blk {BLOCK} -{KEY_TYPE.lower()} -k {KEY}'
    ], capture_output=True, text=True)
    out = rd.stdout.strip()
    print("Proxmark READ:", out)

    read_hex = None
    for line in out.splitlines():
        m = re.search(r'\|\s*([0-9A-F]{2}(?:\s[0-9A-F]{2}){15})\s*\|', line)
        if m:
            read_hex = m.group(1).replace(' ', '')
            break

    if read_hex != hex_payload:
        print("❌ Proxmark verify FAILED\n")
        results.append(['FAIL', read_hex, None])
        continue

    pt = AES.new(AES_KEY, AES.MODE_ECB).decrypt(unhexlify(read_hex))
    print("✅ Proxmark OK → Decrypted:", pt, "\n")
    results.append(['PASS', read_hex, pt])

    # 3) Switch to ASCII waveform mode & set points
    scope.write(':WAVEFORM:FORMAT ASCII');  wait_opc(scope)
    scope.write(f':WAVEFORM:POINTS {POINTS}'); wait_opc(scope)
    print(f"Waveform = ASCII, {POINTS} points")

    # 4) Single-shot capture
    scope.write(':SINGLE'); wait_opc(scope)
    scope.write(':STOP');   wait_opc(scope)
    time.sleep(0.2)

    # 5) Query ASCII values (already in volts)
    try:
        volts = scope.query_ascii_values(':WAVEFORM:DATA?')
        print(f"Captured {len(volts)} samples; head = {volts[:5]}\n")
    except VisaIOError as e:
        print("Error fetching ASCII data:", e, "\n")
        continue

    # 6) Save CSV
    fname = f'waveform_cycle_{cycle}.csv'
    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Sample', 'Voltage_V'])
        for i, v in enumerate(volts):
            writer.writerow([i, v])
    print("💾 Saved", fname, "\n")

    # 7) Optional plot
    plt.figure()
    plt.plot(volts)
    plt.title(f'Cycle {cycle} Waveform')
    plt.xlabel('Sample #')
    plt.ylabel('Voltage (V)')

# Show any plots and close session
if plt.get_fignums():
    plt.show()

scope.close()
print("All results:", results)

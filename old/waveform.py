import csv
from pyvisa import ResourceManager

def save_waveform_to_csv(output_filename='waveform.csv'):
    # Connect to the scope
    rm = ResourceManager()
    scope = rm.open_resource('USB0::2733::470::100969::0::INSTR')

    print(f"📡 Connected to: {scope.query('*IDN?').strip()}")

    # Stop acquisition to freeze data
    scope.write(":STOP")
    scope.write(":WAV:SOUR CHAN1")       # Set waveform source
    scope.write(":WAV:FORM ASCii")       # ASCII format (human-readable)
    scope.write(":WAV:POIN:MODE RAW")    # Full resolution
    scope.write(":WAV:BYT LSBF")         # Byte order, just in case
    scope.write(":WAV:MODE NORM")        # Normal mode (no averaging)

    print("📥 Downloading waveform data from CH1...")

    # Query waveform data
    data = scope.query_ascii_values(":WAV:DATA?")

    print(f"✅ Retrieved {len(data)} samples. Saving to '{output_filename}'...")

    # Save to CSV
    with open(output_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Sample", "Voltage (V)"])
        for i, val in enumerate(data):
            writer.writerow([i, val])

    print("📁 Done! File saved.")

    scope.close()

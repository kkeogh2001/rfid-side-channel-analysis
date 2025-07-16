# Simple example on how to use the RsInstrument module for remote-controlling yor VISA instrument
# Preconditions:
# - Installed RsInstrument Python module (see the attached RsInstrument_PythonModule folder Readme.txt)
# - Installed VISA e.g. R&S Visa 5.12.x or newer

import pyvisa

# Create resource manager using pyvisa-py backend
rm = pyvisa.ResourceManager('@py')

# Connect to the instrument
resource_string = 'USB0::2733::470::100969::0::INSTR'
instr = rm.open_resource(resource_string)
instr.timeout = 5000  # Timeout in milliseconds

# Optional: clear instrument buffer
try:
    instr.clear()
except pyvisa.errors.VisaIOError:
    # Not all instruments support clear; it's safe to ignore this for USB-TMC
    pass

# Query IDN and print info
idn = instr.query('*IDN?')
print(f"\nHello, I am: '{idn.strip()}'")
print(f'PyVISA backend: pyvisa-py')
print(f'Instrument resource: {instr.resource_name}')
# Options and model name parsing (if supported)
idn_parts = idn.strip().split(',')
if len(idn_parts) >= 4:
    print(f'Instrument full model name: {idn_parts[1]}')
    print(f'Serial number: {idn_parts[2]}')
    print(f'Firmware version: {idn_parts[3]}')

# Close the session
instr.close()



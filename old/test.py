import usbtmc

# Connect to the RTB2002
instr = usbtmc.Instrument(0x0aad, 0x01d7)  # R&S Vendor ID, Product ID

# Test identity query
print(instr.ask("*IDN?"))

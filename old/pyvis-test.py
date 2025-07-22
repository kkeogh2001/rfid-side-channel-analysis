import pyvisa

rm = pyvisa.ResourceManager()
print("Available resources:", rm.list_resources())

instr = rm.open_resource('USB0::0x0AAD::0x01D6::100969::INSTR')
instr.timeout = 5000  # 5 seconds

print("IDN:", instr.query("*IDN?"))

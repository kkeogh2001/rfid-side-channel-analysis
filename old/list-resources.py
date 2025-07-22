import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Found VISA resources:", resources)
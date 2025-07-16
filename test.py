from RsInstrument import RsInstrument

# check driver version
RsInstrument.assert_minimum_version('1.102.0')

resource_string = 'USB0::2733::470::100969::0::INSTR'
instr = RsInstrument(resource_string, reset=False, id_query=False)

# disable the calls to clear() that PyVISA-Py can’t handle
instr.clear_buffers_before_each_read = False
instr.clear_buffers_after_each_read  = False

idn = instr.query_str('*IDN?')
print("IDN:", idn.strip())

instr.close()

import filecmp
import io
import time

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pyvisa.util
from pyvisa.constants import *
import util_rs
from waveform import save_waveform_to_csv


def test_bed(name):

    visaResource = 'USB0::2733::470::100969::0::INSTR'

    # monkey patch to cover the binary transfer (>1GB) for the R&S header
    pyvisa.util.parse_ieee_block_header = util_rs.parse_rs_block_header

    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(resource_name=visaResource)

    # visaManufacturer = instrument.get_visa_attribute(VI_ATTR_RSRC_MANF_NAME)
    # visaVersion = instrument.get_visa_attribute(VI_ATTR_RSRC_IMPL_VERSION)
    # print("visa lib manufacturer\t:: %s\nVisa version\t\t:: %06x\n" % (visaManufacturer, visaVersion))


    instrument.write('*CLS; *ESE 255')
    out = instrument.query('*IDN?')
    print("instrument ID is :: %s" % out)

    # instrument.timeout=20000
    instrument.write('MMEMory:CDIRectory "/INT/SETTINGS"')
    print(instrument.query('SYSTem:ERRor:ALL?'))

    catEntries = instrument.query('MMEMory:CATalog:LENGth?')
    print("CATalog:LENGth? :: %s" % catEntries)

    out = instrument.query('MMEMory:CATalog?')
    print('DIR :: %s' % out)

    out = instrument.query_binary_values('MMEMory:DATA? "DWNLTEST.SET"', datatype='B')
    outData = bytearray(out)
    with open('DWNLTEST.SET', 'wb') as f:
        f.write(outData)
    print(instrument.query('SYSTem:ERRor:ALL?'))

    result = filecmp.cmp('DWNLTEST.SET', 'DWNLTEST.ORIG.SET', shallow=False)
    if result:
        print(result)

    with open('DWNLTEST.SET', 'rb') as f:
        inData = f.read()
    instrument.write_binary_values('MMEMory:DATA "DWNLTSNW.SET",', inData, datatype='B')

    out = instrument.query('MMEMory:CATalog?')
    print(out)
    print(instrument.query('SYSTem:ERRor:ALL?'))

    instrument.write('HCOPy:LANGuage PNG')
    # processing takes longer, so the timeout is increased temporarily
    timeout_prev = instrument.get_visa_attribute(VI_ATTR_TMO_VALUE)
    instrument.set_visa_attribute(VI_ATTR_TMO_VALUE, timeout_prev*2)
    out = instrument.query_binary_values('HCOPy:DATA?', datatype='B')
    instrument.set_visa_attribute(VI_ATTR_TMO_VALUE, timeout_prev)
    outData = bytearray(out)
    image = Image.open(io.BytesIO(outData))
    image.show()
    print(instrument.query('SYSTem:ERRor:ALL?'))
    with open('SCRSHOT.PNG', 'wb') as f:
        f.write(outData)

    instrument.write('RUNS')
    instrument.write('FORMat:DATA REAL,32')
    if instrument.query('FORMat:BORDer?') == 'MSBF\n':
        endianess = True
    else:
        endianess = False
    ooo = instrument.query_binary_values('CHANnel2:DATA?', datatype='f', container=np.array, is_big_endian=endianess)
    plt.plot(ooo)
    print(instrument.query('SYSTem:ERRor:ALL?'))

    instrument.close()

    # small instrument do not have a large acquisition memory, so switching to another instrument
    visaResource = 'TCPIP::rtp164-103229::INSTR'

    instrument = rm.open_resource(resource_name=visaResource)
    instrument.write('*CLS; *ESE 255')

    instrument.write('FORMat:DATA REAL,32')
    if instrument.query('FORMat:BORDer?') == 'MSBF\n':
        endianess = True
    else:
        endianess = False

    instrument.write('*CLS')  # clear the status bytes
    instrument.write('RUNSingle; *OPC')
    esrInSTB = instrument.read_stb()
    while not (esrInSTB & (1 << 5)):
        esrInSTB = instrument.read_stb()
        time.sleep(0.5)
    esr = instrument.query('*ESR?')

    ooo = instrument.query_binary_values('CHANnel2:DATA?', datatype='f', container=np.array, is_big_endian=endianess)
    plt.plot(ooo)
    print(instrument.query('SYSTem:ERRor:ALL?'))

    instrument.close()

    # visaResource = 'TCPIP::fsw-101241::INSTR'
    #
    # instrument = rm.open_resource(resource_name=visaResource)
    # instrument.write('*CLS; *ESE 255')
    #
    # print(instrument.query('SYSTem:ERRor?'))
    #
    # instrument.write('FORMat:DATA REAL,32')
    #
    # ooo = instrument.query_binary_values('TRAC:DATA? TRACE1', datatype='f', container=np.array, is_big_endian=False)
    # plt.plot(ooo)
    #
    # instrument.close()

    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # test_bed('visa binary transfer')
    save_waveform_to_csv("my_waveform.csv")


exit(0)

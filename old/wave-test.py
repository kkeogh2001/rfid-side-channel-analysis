from pyvisa import ResourceManager, constants

rm = ResourceManager()
scope = rm.open_resource(
  'ASRL/dev/ttyACM0::INSTR',
  baud_rate=115200,
  data_bits=8,
  parity=constants.Parity.none,
  stop_bits=constants.StopBits.one,
  timeout=10000
)
# make sure the terminations match the scope
scope.read_termination  = '\n'
scope.write_termination = '\n'

print(scope.query('*IDN?'))   # should now return your RTB2002 ID

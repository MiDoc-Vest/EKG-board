import sys
import io
import serial
import base64
import numpy as np



SERIAL_PORT_PATH = "/dev/ttyACM0"  # your actual path to the Arduino Native serial port device goes here
baudrate=115200

raw_serial_port = serial.serial_for_url(SERIAL_PORT_PATH, baudrate=baudrate, timeout=0.1)
raw_serial_port.reset_input_buffer()
serial_port = io.TextIOWrapper(io.BufferedRWPair(raw_serial_port, raw_serial_port))

serial_port.write("rdatac\n")
serial_port.flush()
response = serial_port.readline()
while response != "200 Ok\n":
  response = serial_port.readline()

#'Received: rdatac\n'
channels = np.zeros((8, 1000))

while True:
  channels[:,0:999] = channels[:,1:1000]  # Shift data over one timestep

  # Read data from EKG
  response = serial_port.readline()
  decoded_response = base64.b64decode(response)
  timestamp = int.from_bytes(decoded_response[0:4], "big")
  sample_number = int.from_bytes(decoded_response[4:8], "big")

  # Store channel info
  for i in range(8):
    channels[i,999] = int.from_bytes(decoded_response[8+3*i:11+3*i], "big")

  for i in range(8):
    print("Channel %d: %d" % (i, channels[i,999]))
  print("\n")
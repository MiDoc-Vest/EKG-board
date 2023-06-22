import sys
import io
import serial
import base64
import numpy as np
import matplotlib.pyplot as plt
import ecg_plot

VDD = 3.3
VSS = -2.5

def calculate_12_lead(channels):
  # Expect array of 8 values in channels: V6, leadI, leadII, V2, V3, V4, V5, V1

  # Adjust channels to be in correct range
  channels = (channels / 2^24) * ((VDD * VSS) / 2)

  # Calculate leads I, II, III
  leadI = channels[1]
  leadII = channels[2]
  leadIII = leadII - leadI

  # Calculate leads aVR, aVL, aVF
  aVR = -(leadI + leadII) / 2
  aVL = leadI - leadII / 2
  aVF = leadII - leadI / 2

  # Calculate leads V1, V2, V3, V4, V5, V6
  V1 = channels[7]
  V2 = channels[3]
  V3 = channels[4]
  V4 = channels[5]
  V5 = channels[6]
  V6 = channels[0]

  # Return array of 12 values in leads: V1, V2, V3, V4, V5, V6, leadI, leadII, leadIII, aVR, aVL, aVF
  return [V1, V2, V3, V4, V5, V6, leadI, leadII, leadIII, aVR, aVL, aVF]

SERIAL_PORT_PATH = "/dev/cu.usbmodem1441301"  # your actual path to the Arduino Native serial port device goes here
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
x = np.arange(0, 1000)
fig = plt.figure()
ax = fig.add_subplot(111)

plt.ion()
plt.ylim([0, 20000000])
fig.show()

# Plot each row of channels as line
lines = [None] * 8

for i in range(1000):
  # Read data from EKG
  response = serial_port.readline()
  decoded_response = base64.b64decode(response)
  timestamp = int.from_bytes(decoded_response[0:4], "big")
  sample_number = int.from_bytes(decoded_response[4:8], "big")

  # Store channel info
  for j in range(8):
    channels[j, i] = int.from_bytes(decoded_response[8+3*i:11+3*i], "big")

# for i in range(8):
#   lines[i], = ax.plot(x, channels[i,:])
# fig.canvas.draw()
# fig.canvas.flush_events()

ecg_12_lead = calculate_12_lead(channels)

ecg_plot.plot(ecg_12_lead, sample_rate=250, title="ECG-12")
ecg_plot.show()
ecg_plot.save_as_png("example_ecg")

  # for i in range(8):
  #   print("Channel %d: %d" % (i, channels[i,999]))
  # print("\n")
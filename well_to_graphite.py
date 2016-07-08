import serial
import re
import argparse
import os

# distance from sensor to water min level
zero_level = 131
graphite_namespace = 'smarthouse.sensors.well.level'

# FIR Class to average


class Fir(object):
    def __init__(self, length):
        self.fir = []
        self.cnt = 0
        self.length = length
        for _ in range(self.length):
            self.fir.append(0)

    def put(self, data):
        self.fir[self.cnt] = data
        if self.cnt == (self.length-1):
            self.cnt = 0
        else:
            self.cnt += 1

    def average(self):
        avr = 0
        for i in self.fir:
            avr += i
        return avr/self.length


parser = argparse.ArgumentParser(
            description='Get the well water level and send it to Graphite')
parser.add_argument('--host',
                    help='Graphite server address',
                    required=True)
parser.add_argument('--port', '-p',
                    help='Graphite server port (default - 2003)',
                    default=2003)
parser.add_argument('--serial_port',
                    help='Serial port name to receive data (default - /def/ttyUSB0)',
                    default='/dev/ttyUSB0')
parser.add_argument('--serial_speed',
                    help='Serial port speed to receive data (default - 115200)',
                    default=115200)
parser.add_argument('--average', '-a',
                    help='Points to average (default - 100)',
                    default=100)
parser.add_argument('--verbose', '-v',
                    help='Verbose mode',
                    action='store_true')

args = parser.parse_args()


ser = serial.Serial(args.serial_port, args.serial_speed, timeout=20)
fir = Fir(args.average)

while True:
    line = ser.readline()
    searchObj = re.search(b'distance: ([0-9]+) ', line, re.M | re.I)
    if searchObj:
        depth = zero_level - int(searchObj.group(1))/58.0
        fir.put(depth)
        avr = fir.average()
        message = '{{"depth": {0:3.1f}}}'.format(depth)
        cmd = 'echo "{0} {1:3.1f} `date +%s`" | nc -q0 {2} {3}'.format(
            graphite_namespace, avr, args.host, args.port)
        if args.verbose:
            print(message, "{0:3.1f}".format(avr))
            print(cmd)

        os.system(cmd)

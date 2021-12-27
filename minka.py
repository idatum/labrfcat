import sys
import os
import time
import rflib
import logging
import argparse
import struct

Log = logging.getLogger('minka')
MaxPower = False
Freq = 304320000
Baud = 2400
# Spacer bytes plus packet bytes
PktLen = 10

# Minka Aire remote (TR110A)
# ASK/OOK octal encoding with bit 0 == 010, bit 1 == 110
# Pulse length is about 2.49ms, with 13 pulses per packet.
# All packets have aleading 010 octal, followed by octals
# for SW8 and SW9, and the command octals.
PREAMBLE = '010'
# Remote battery compartment has 2 jumper switches:
# SW8 switch has 4 octals representing setting
# e.g. off off off off
SW8 = '010010010010'
# SW9 has 4 octals representing setting
# e.g off off on on
SW9 = '010010110110'
# Fan commands are 4 octals.
OFF = '110010110010'
SLOW = '010010110010'
MED = '010110010010'
FAST = '110010010010'
# Light has one command and toggles on/off.
# NOTE: if remote held down, cycles through dimming/brigthening light.
LIGHT = '010110010110'
# arg options
CMDS = {'off': OFF,
        'slow': SLOW,
        'medium': MED,
        'fast': FAST,
        'light': LIGHT}
# Send 5 bytes of all 0 between xmits as spacing.
SPACE = b'\x00\x00\x00\x00\x00'


def initRadio(d):
    d.setFreq(Freq)
    if MaxPower:
        d.setMaxPower()
    d.setMdmModulation(rflib.MOD_ASK_OOK)
    d.setMdmDRate(Baud)
    d.makePktFLEN(PktLen)
    d.setMdmSyncMode(0)


def fanCmd(d, CMD):
    try:
        initRadio(d)
        # string octal bits together for full packet of 39 bits
        bits = PREAMBLE + SW8 + SW9 + CMD
        # pack octal bits into byte string with leading spacing
        data = SPACE + \
               b''.join([struct.pack('B', int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)])
        Log.debug(data)
        for i in range(0, 8):
            d.RFxmit(data)
    finally:
        d.setModeIDLE()
        d.cleanup()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", required=False, action='store_true', default=False, help="Enable debugging output.")
    ap.add_argument("--max", required=False, action='store_true', default=False, help="Max power.")
    ap.add_argument("--sw8", required=False, action='store', default=SW8, help="Bits representing SW8")
    ap.add_argument("--sw9", required=False, action='store', default=SW9, help="Bits representing SW9")
    ap.add_argument("--cmd", required=True, action='store', help="off, slow, medium, fast, or light")
    args = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    MaxPower = args.max
    if args.cmd not in CMDS:
        Log.error(f'{args.cmd} is invalid.')
        sys.exit(2)
    Log.info(args.cmd)
    d = rflib.RfCat()
    time.sleep(1)
    fanCmd(d, CMDS[args.cmd])


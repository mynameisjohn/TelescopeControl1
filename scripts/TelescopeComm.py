import serial
import asyncio
import copy

# Telescope serial communication class
class TelescopeComm:
    # When the mount is done, it returns a '#' byte
    STOPCHAR = b'#'
    STOPBYTE = ord(b'#')

    # Take in the device port as ctor arg
    def __init__(self, strDevice):
        # Create serial object
        self.ser = serial.Serial()
        self.ser.port = strDevice
        self.ser.baudrate = 9600
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE

        # Set our cur speed to zero
        self.nAltSpeed = 0
        self.nAzmSpeed = 0

        # Open the serial port, handle exception if unable to open
        try:
            self.ser.open()
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            raise RuntimeError('Error: Unable to open serial port!')

        # Read back an echo value to test
        echoInput = bytearray([ord('K'), 69])
        expectedResp = bytearray([69, TelescopeComm.STOPBYTE])
        if self._executeCommand(echoInput) != expectedResp:
            raise RuntimeError('Error: unable to communicate with telescope!')

        # Success
        print('Telescope found at port', strDevice)

    # Slew at a variable rate (nSpeed in arcseconds)
    def slewVariable(self, strID, nSpeed):
        # Command needs high precision and low precision separate
        trackRateHigh = (4 * nSpeed) / 256
        trackRateLow = (4 * nSpeed) % 256

        # Positive / Negative altitude / azimuth
        cmdDict = {
            'Alt+' : [3, 17, 6, abs(trackRateHigh), abs(trackRateLow)],
            'Alt-' : [3, 17, 7, abs(trackRateHigh), abs(trackRateLow)],
            'Azm+' : [3, 16, 6, abs(trackRateHigh), abs(trackRateLow)],
            'Azm-' : [3, 16, 7, abs(trackRateHigh), abs(trackRateLow)]
        }
        return self._slewCommand(strID, cmdDict)

    # sends a slew command to the mount
    # strID should be Alt or Azm, nSpeed is a signed int
    def slewFixed(self, strID, nSpeed):
        # Positive / Negative altitude / azimuth
        cmdDict = {
            'Alt+' : [2, 17, 36, abs(nSpeed)],
            'Alt-' : [2, 17, 37, abs(nSpeed)],
            'Azm+' : [2, 16, 36, abs(nSpeed)],
            'Azm-' : [2, 16, 37, abs(nSpeed)]
        }
        return self._slewCommand(strID, cmdDict)

    # Implementation of command for fixed and variable rates
    # assumes it will get a dict with positive/negative denoted by last char
    def _slewCommand(self, strID, cmdDict):
        # Create local copy of string, append '+' or '-' depending
        strID = copy.copy(strID)
        if strID == 'Alt' or strID == 'Azm':
            # Store local speed values as well
            if strID == 'Alt':
                self.nAltSpeed = nSpeed
            else:
                self.nAzmSpeed = nSpeed

            # Append '+' or '-' depending on sign
            strID += '+' if nSpeed > 0 else '-'

            # Create command bytes
            cmdData = cmdDict[strID]
            cmdSlew = bytearray([ord('P'), 0, 0, 0, 0, 0, 0, 0])
            cmdSlew[1:len(cmdData) + 1] = bytearray(cmdData)

            # execute command and return True (should check resp)
            resp = self._executeCommand(cmdSlew)
            return True

        # Return false if not handled properly
        return False

    def GetPosition(self):
        # Send get AZM-ALT command (not precise)
        resp = self._executeCommand(bytearray([ord('Z')]))
        # Sanity check
        if len(resp) == 0 or resp[-1] != TelescopeComm.STOPBYTE:
            raise RuntimeError('Error: Invalid response from get AZM-ALT command!')
        # Strip stop byte and split by comma and unpack
        azmResp, altResp = *(resp[0:len(resp)-1].split(','))
        # values are two 16 bit ints as hex string
        azm = int(azmResp, 16)
        alt = int(altResp, 16)
        return [azm, alt]

    # Internal function that sends a serial
    # command and waits for the stop byte
    def _executeCommand(self, cmd):
        # Send the command
        self.ser.write(cmd)

        # Read in the response until chResp is the stop byte
        bufResp = []
        chResp = None

        # Only try to read 100 chars
        for i in range(100):
            bufResp.append(self.ser.read())
            if bufResp[-1] == TelescopeComm.STOPCHAR:
                break
        # We "timed out"
        else:
            raise RuntimeError('Error: stop char not recieved!')

        # Return the response
        return bytearray(ord(b) for b in bufResp)

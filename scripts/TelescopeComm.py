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

        # Open the serial port, handle exception if unable to open
        try:
            self.ser.open()
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            raise RuntimeError('Error: Unable to open serial port!')

        # Read back an echo value to test
        echoInput = bytearray([ord('K'), 69])
        expectedResp = bytearray([69, TelescopeComm.STOPBYTE])
        resp = bytearray(ord(b) for b in self._executeCommand(echoInput))
        print(echoInput, expectedResp, resp)
        if resp != expectedResp:
            raise RuntimeError('Error: unable to communicate with telescope!')

    # sends a slew command to the mount
    # strID should be Alt or Azm, nSpeed is a signed int
    def slew(self, strID, nSpeed):
        # Positive / Negative altitude / azimuth
        cmdDict = {
            'Alt+' : (2, 17, 36, nspeed),
            'Alt-' : (2, 17, 37, nspeed),
            'Azm+' : (2, 16, 36, nspeed),
            'Azm-' : (2, 16, 37, nspeed)
        }

        # Create local copy of string, append '+' or '-' depending
        strID = copy.copy(strID)
        if strID is 'Alt' or strID is 'Azm':
            # Store local speed values as well
            if strID is 'Alt':
                self.nAltSpeed = nSpeed
            else:
                self.nAzmSpeed = nSpeed

            # Append '+' or '-' depending on sign
            strID.append('+' if nSpeed > 0 else '-')

            # Create command bytes
            cmdSlew = bytearray([ord('P'), 0, 0, 0, 0, 0, 0, 0])
            #cmdSlew[1:] = *cmdDict[strID]

            # execute command and return True
            self._executeCommand(cmdSlew)
            return True

        # Return false if not handled properly
        return False

    # Close port if open on deletion
    def __del__(self):
        if self.ser.isOpen():
            self.ser.close()

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
        return bufResp

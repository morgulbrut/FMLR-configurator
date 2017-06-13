from appJar import gui
import serial
import logging
import Colorer
import time

log_level = logging.INFO
FORMAT = '%(levelname)-8s %(message)s'

# function called by pressing the buttons
def press(btn):
    global ser
    if btn=='Cancel':
        ser.close()
        app.stop()
    elif btn=='Connect':
        connect_uart()
    elif btn == 'Submit':
        submit_vals()

def connect_uart():
    global ser
    port = app.getEntry('serial')
    print('Connecting to: '+ port)
    try:
        ser.port = port
        ser.baudrate=115200
        ser.open()
        read_vals()
    except serial.serialutil.SerialException as e:
        error=str(e)
        print(error)
        if error.find('PermissionError',len(error)):
            logging.critical('Could not open Port ' +port)
        elif error.find('FileNotFoundError',len(error)):
            logging.critical('Port ' +port+ ' don\'t exist')

def read_vals():
    app.infoBox('Reset board','Please reset your conncted board after closing this message')
    logging.info('Waiting for console....')
    wait_for('$')
    print(get_available_cmds())

def get_available_cmds():
    send_cmd('AT?')

    test='''<LF>AT+<CMD>         : Run <CMD>
<LF>AT+<CMD>=<value> : Set the value
<LF>AT+<CMD>=?       : Get the value
<LF>Z: Trig a reset of the MCU
<LF>+VER: Get the version of the AT configuration
<LF>+DEUI: Get the Device EUI
<LF>+DADDR: Get or Set the Device address
<LF>+APPKEY: Get or Set the Application Key
<LF>+NWKSKEY: Get or Set the Network Session Key
<LF>+APPSKEY: Get or Set the Application Session Key
<LF>+APPEUI: Get or Set the Application EUI
<LF>+ADR: Get or Set the Adaptive Data Rate setting. (0: off, 1: on)
<LF>+CYCLE: Get or Set the application cycle time in [ms]
<LF>+PORT: Get or Set the application port
<LF>+DCS: Get or Set the ETSI Duty Cycle setting - 0=disable, 1=enable - Only for testing
<LF>+NJM: Get or Set the Network Join Mode. (0: ABP, 1: OTAA)
<LF>+NWKID: Get or Set the Network ID
<LF>+CFM: Get or Set the confirmation mode (0-1)
<LF>+SCYCLE: Get or Set how many measurement to send at once
    '''
    cmds = test.splitlines()

    return cmds

def wait_for(char):
    while True:
        data_raw = ser.readline()
        if data_raw:
            data = data_raw.decode('utf-8').strip()
            logging.debug(data)
            if data == char:
                logging.debug(char)
                return data
            if data == 'AT_ERROR':
                return data
            if data == 'AT_PARAM_ERROR'.encode('utf-8'):
                return data
            if data == 'AT_BUSY_ERROR':
                return data
            if data == 'AT_TEST_PARAM_OVERFLOW':
                return data
            if data == 'AT_NO_NETWORK_JOINED':
                return data
            if data == 'AT_RX_ERROR':
                return data

def reset_module():
    ser.write(bytes('ATZ' + '\r\n', 'utf-8'))


def write_cmd(cmd, ans):
    logging.info(cmd.upper())
    ser.write(bytes(cmd + '\r\n'.upper(), 'utf-8'))
    if wait_for(ans) == ans:
        pass
    else:
        logging.critical(wait_for(ans))

def submit_vals():
    values = app.getAllEntries()
    for val in values:
        if (val != 'serial'):
            cmd = 'AT+'+ val + '=' + values[val]
            write_cmd(cmd,'OK')
    for i in ['ADR','NJM','CFM']:
        if app.getCheckBox(i):
            cmd = 'AT' + i + '=1'
        else:
            cmd = 'AT' + i + '=0'
        write_cmd(cmd,'OK')


ser=serial.Serial()

app = gui('FMLR Configurator', '1024x400')
app.setIcon('Graphicloads-100-Flat-Settings-3.ico')

app.addLabel('serial','UART',0,2)
app.addEntry('serial', 0, 3)
app.addButton('Connect',press,0,4)

app.addLabel('deui', 'Device EUI:', 1, 0)
app.addEntry('deui', 1, 1)
app.addLabel('appeui', 'App EUI:', 2, 0)
app.addEntry('appeui', 2, 1)
app.addLabel('appkey', 'Appkey:', 3, 0)
app.addEntry('appkey', 3, 1)


app.addLabel('daddr', 'Device address:', 1, 2)
app.addEntry('daddr', 1, 3)
app.addLabel('nwkskey', 'Networksession key:', 2, 2)
app.addEntry('nwkskey', 2, 3)
app.addLabel('appskey', 'Appsession key:', 3, 2)
app.addEntry('appskey', 3, 3)

app.addCheckBox('NJM',4,0)
app.addLabel('njm', 'Tick for OTAA, untick for ABP',4,1)
app.addCheckBox('ADR',5,0)
app.addLabel('adr', 'Tick for adaptive data rate',5,1)
app.addCheckBox('CFM',4,2)
app.addLabel('cfm', 'Tick for confirmated messages',4,3)

app.addLabel('cycle', 'Application cycle time:', 15, 0)
app.addEntry('cycle', 15, 1)

app.addLabel('port', 'Port:', 15, 2)
app.addEntry('port', 15, 3)

app.addButton('Cancel', press, 21, 3)
app.addButton('Submit', press, 21, 4)

app.setEntryFocus('serial')

app.go()


'''

import serial
import binascii
import logging
import Colorer
import argparse
import csv
from enum import Enum
import time

class AgumentType(Enum):
    FILE = 1

type = 'AT'
serial_timeout = .3

ser = serial.Serial()
if type == 'AT':
    ser._baudrate = 115200
else:
    ser._baudrate = 57600
ser.port = 'COM17'
ser.timeout = serial_timeout

log_level = logging.INFO
FORMAT = '%(levelname)-8s %(message)s'


def addparser_init():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        help='input csv file with test cases: <command>, <response>')
    parser.add_argument('--debug',
                        action='store_true',
                        help='set logging level to DEBUG')
    return parser


def parse_arguments(parser):
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=log_level, format=FORMAT)
    if args.i:
        return [AgumentType.FILE, args.i]


def read_csv_file(file):
    try:
        f = open(file, 'rt')
        return csv.reader(f)
    except FileNotFoundError:
        logging.critical(file + ': File not found')
    except IndexError:
        logging.critical(file + ': File not formated well')

def parse_row(row):
    try:
        if row[0].strip()[:1] == '#':
            pass
        elif row[0] == 'pause':
            pause(row[1])
        elif row[0] == 'msg':
            print('[MESSAGE]' + row[1].strip())
        elif row[0] == 'wait':
            wait_for(row[1].strip())
        else:
            if len(row) == 3:
                ser.timeout = float(row[2].strip())
            else:
                ser.timeout = serial_timeout
            test_command(row[0].strip(), row[1].strip())
    except IndexError:
        pass


def parse_csv(reader):
    for row in reader:
        parse_row(row)


def connect_serial():
    try:
        ser.open()
        ser.flushInput()
        ser.flushOutput()
        return True
    except serial.serialutil.SerialException as e:
        logging.critical(e)
        return False


def test_command(cmd, ans):
    logging.debug('[Test]: ' + cmd + ' -> ' + ans)
    send_command(cmd)
    resp = ser_read(ans)
    if resp[0]:
        logging.info('[' + cmd + ' -> ' + ans + ']-> ' + resp[1] + '-> PASSED')
    else:
        try:
            logging.error('[' + cmd + ' -> ' + ans + ']-> ' + resp[1] + '-> FAILED')
        except TypeError:
            logging.critical('No valid response, is the modem running?')


def pause(secs):
    print('[Pause]: ' + secs +" sec")
    time.sleep(float(secs))


def send_command(cmd):
    logging.debug('[TX]: ' + cmd)
    cmd = cmd + '\r\n'
    ser.flushOutput();
    #ser.flushInput();
    try:
        ser.write(bytes(cmd, 'utf-8'))
    except serial.serialutil.SerialException as e:
        logging.critical(e)


def wait_for(ans):
    try:
        print('[WAITING] for ' + ans)
        while True:
            data_raw = ser.readline()
            if data_raw:
                data = data_raw.decode('utf-8').strip()
                logging.debug(data)
                if data == ans:
                    return 'found'
    except serial.serialutil.SerialException as e:
        logging.critical(e)


def ser_read(ans):
    try:
        rx = ser.readline()
        old_rx = rx
        while rx:
            if type == 'AT':
                rx = rx.decode('utf-8').replace('\n', '').replace('\r', '')
            else:
                rx = rx.decode('utf-8').replace('\n', '').replace('\n', '')
            logging.debug('[RX]: ' + rx)
            if type == 'AT':
                if rx == ans:
                    return [True, rx]
            else:
                if rx.split(':')[0] == ans:
                    return [True, rx]
            if len(rx) > 0:
                    old_rx = rx
            rx = ser.readline()
        return [False, old_rx]
    except serial.serialutil.SerialException as e:
        logging.critical(e)


def main():
    if connect_serial():
        args = parse_arguments(addparser_init())
        if args[0] == AgumentType.FILE:
            reader = read_csv_file(args[1])
            parse_csv(reader)

if __name__ == "__main__":
    main()
'''
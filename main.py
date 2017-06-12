from appJar import gui
import serial
import logging
import Colorer

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

def submit_vals():
    values = app.getAllEntries()
    for val in values:
        if (val != 'serial'):
            cmd = 'AT+'+ val + '=' + values[val]
            send_cmd(cmd)
    for i in ['ADR','NJM','CFM']:
        if app.getCheckBox(i):
            cmd = 'AT' + i + '=1'
        else:
            cmd = 'AT' + i + '=0'
        send_cmd(cmd)


def send_cmd(cmd):
    print((cmd + '\n\r').strip().upper())
    #ser.write(bytes(cmd+'\n\r').strip().upper())

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
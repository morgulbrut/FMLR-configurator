# !/usr/bin/env python
# encoding: utf-8

from enum import Enum
import serial
import argparse
import logging
import Colorer
import csv


class AgumentType(Enum):
    FILE = 1


log_level = logging.INFO
FORMAT = '%(levelname)-8s %(message)s'

header = []

serial_timeout = 0.1
ser = serial.Serial()
ser._baudrate = 115200
ser.port = 'COM11'
ser.timeout = serial_timeout


def addparser_init():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        help='input csv file')
    parser.add_argument('-p',
                        help='Serial port')
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
    if args.p:
        ser.port = args.p
        print(args.p)
    if args.i:
        return [AgumentType.FILE, args.i]


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
        else:
            logging.info('Waiting for console....')
            wait_for('$')
            for i in range(len(row)):
                if row[i]:
                    write_cmd('AT+' + header[i].strip() + '=' + row[i].strip(), 'OK')
            logging.info('Comissioning done, please reset module')
    except IndexError:
        pass


def reset_module():
    ser.write(bytes('ATZ' + '\r\n', 'utf-8'))


def write_cmd(cmd, ans):
    logging.info(cmd.upper())
    ser.write(bytes(cmd + '\r\n'.upper(), 'utf-8'))
    if wait_for(ans) == ans:
        pass
    else:
        logging.critical(wait_for(ans))


def connect_serial():
    try:
        ser.open()
        ser.flushInput()
        ser.flushOutput()
        return True
    except serial.serialutil.SerialException as e:
        logging.critical(e)
        return False


def parse_csv(reader):
    global header
    header = next(reader)
    for row in reader:
        parse_row(row)


def main():
    if connect_serial():
        args = parse_arguments(addparser_init())
        if args[0] == AgumentType.FILE:
            logging.info('Comissioning started')
            reader = read_csv_file(args[1])
            parse_csv(reader)


if __name__ == "__main__":
    main()

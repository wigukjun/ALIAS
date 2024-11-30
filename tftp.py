#!/usr/bin/python3
'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''
import os
import sys
import socket
import argparse
# import validators
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
MODE = {'netascii': 1, 'octet': 2, 'mail': 3}

ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}


def send_wrq(filename, mode):
    pass


def send_rrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes                         (mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    #print(rrq_message)


def send_ack(seq_num, server):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    print(seq_num)
    print(ack_message)


# parse command line arguments
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str)
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()

# if validators.domain(args.host):
#     server_ip = gethostbyname(args.host)
# else
#     server_ip = args.host
# if args.port == None:
#     server_port = DEFAULT_PORT


# Create a UDP socket
server_ip = args.host
server_port = DEFAULT_PORT
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

# Send RRQ_message
send_rrq(filename, mode)

# Open a file to save data from server
file = open(filename, 'wb')
expected_block_number = 1

while True:
    # receive data from the server
    # server uses a newly assigned port(not 69)to transfer data
    # so ACK should be sent to the new socket
    data, server_new_socket = sock.recvfrom(516)
    opcode = int.from_bytes(data[:2], 'big')

    # check message type
    if opcode == OPCODE['DATA']:
        block_number = int.from_bytes(data[2:4], 'big')
        if block_number == expected_block_number:
            send_ack(block_number, server_new_socket)
            file_block = data[4:]
            file.write(file_block)
            expected_block_number = expected_block_number + 1
            print(file_block.decode())
        else:
            send_ack(block_number, server_new_socket)

    elif opcode == OPCODE['ERROR']:
        error_code = int.from_bytes(data[2:4], byteorder='big')
        print(ERROR_CODE[error_code])
        file.close()
        os.remove(filename)
        break

    else:
        break

    if len(file_block) < BLOCK_SIZE:
        file.close()
        #print(len(file_block))
        print("File transfer completed")
        break

s.bind(('', 9262))
s.settimeout(5)
while True:
    try:
        print('Received ACK from server')
        data, address = s.recvfrom(512)
    except socket.timeout:
        print("Timeout")
sys.exit(0)
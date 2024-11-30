#!/usr/bin/python3
"""
TFTP 클라이언트 프로그램
$ mytftp host_address [get|put] filename
"""
import socket
import argparse
from struct import pack, unpack
import os

# 기본 설정
DEFAULT_PORT = 69
BUFFER_SIZE = 516  # 데이터 블록(512 bytes) + 헤더(4 bytes)
BLOCK_SIZE = 512
DEFAULT_MODE = 'octet'

# TFTP 명령 및 에러 코드
OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
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

# 함수 정의
def send_request(sock, server_address, operation, filename, mode):
    """ RRQ 또는 WRQ 요청 전송 """
    opcode = OPCODE['RRQ'] if operation == 'get' else OPCODE['WRQ']
    request_packet = pack(f">H{len(filename)}sB{len(mode)}sB", opcode, filename.encode(), 0, mode.encode(), 0)
    sock.sendto(request_packet, server_address)


def send_ack(sock, block_number, server_address):
    """ ACK 전송 """
    ack_packet = pack(">HH", OPCODE['ACK'], block_number)
    sock.sendto(ack_packet, server_address)


def receive_file(sock, server_address, filename):
    """ 파일 다운로드 (GET) """
    with open(filename, 'wb') as file:
        expected_block = 1
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                opcode, block_number = unpack(">HH", data[:4])
                if opcode == OPCODE['DATA']:
                    if block_number == expected_block:
                        file.write(data[4:])
                        send_ack(sock, block_number, addr)
                        expected_block += 1
                    if len(data) < BUFFER_SIZE:
                        print(f"Download completed: {filename}")
                        break
                elif opcode == OPCODE['ERROR']:
                    error_code = unpack(">H", data[2:4])[0]
                    print(f"Error: {ERROR_CODE.get(error_code, 'Unknown error')}")
                    break
            except socket.timeout:
                print("Timeout while receiving data.")
                break


def send_file(sock, server_address, filename):
    """ 파일 업로드 (PUT) """
    try:
        with open(filename, 'rb') as file:
            block_number = 1
            while True:
                data = file.read(BLOCK_SIZE)
                data_packet = pack(">HH", OPCODE['DATA'], block_number) + data
                sock.sendto(data_packet, server_address)
                try:
                    ack, addr = sock.recvfrom(BUFFER_SIZE)
                    opcode, recv_block_number = unpack(">HH", ack[:4])
                    if opcode == OPCODE['ACK'] and recv_block_number == block_number:
                        block_number += 1
                    if len(data) < BLOCK_SIZE:
                        print(f"Upload completed: {filename}")
                        break
                except socket.timeout:
                    print("Timeout while sending data.")
                    break
    except FileNotFoundError:
        print(f"File not found: {filename}")


def main():
    parser = argparse.ArgumentParser(description="TFTP Client")
    parser.add_argument("host", help="TFTP server IP address")
    parser.add_argument("operation", choices=['get', 'put'], help="Operation: get or put")
    parser.add_argument("filename", help="Filename to transfer")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, help="TFTP server port (default: 69)")
    args = parser.parse_args()

    server_address = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    if args.operation == 'get':
        send_request(sock, server_address, 'get', args.filename, DEFAULT_MODE)
        receive_file(sock, server_address, args.filename)
    elif args.operation == 'put':
        send_request(sock, server_address, 'put', args.filename, DEFAULT_MODE)
        send_file(sock, server_address, args.filename)

    sock.close()


if __name__ == "__main__":
    main()

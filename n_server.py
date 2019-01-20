#!/usr/bin/env python3

import socket
import sys
import select
import tty
import termios


def main():
    host = ''
    port = 9999
    s = None

    try:
        s = socket.socket()  # actual conversation between server and client
    except socket.error as msg:
        print("Error creating socket: " + str(msg))

    try:
        print("Binding socket to port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Error binding socket to port: " + str(msg))

    conn, address = s.accept()
    s.setblocking(False)

    print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))

    oldtty = termios.tcgetattr(sys.stdin)

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())

        while True:
            r, w, e = select.select([conn, sys.stdin], [], [])

            if sys.stdin in r:
                byte = sys.stdin.buffer.read(1)
                conn.send(byte)

            if conn in r:
                recv_data = conn.recv(1024)
                # print("Received: ", recv_data.decode('utf8'))
                sys.stdout.buffer.write(recv_data)
                sys.stdout.flush()

    finally:
        conn.close()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


main()

#!/usr/bin/env python
#coding:utf-8

import socket

server_ip = '127.0.0.1'
server_port = 6666

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server_ip, server_port))
    print 'Connecting to Server: %s:%d' % (server_ip, server_port)
    print server_socket.recv(1024)
    server_socket.send('you are a bitch')
    server_socket.close()

if __name__ == '__main__':
    main()
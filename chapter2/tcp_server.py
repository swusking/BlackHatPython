#!/usr/bin/env python
#coding:utf-8

import socket
import threading

bind_ip = '0.0.0.0'
bind_port = 6666

def client_process(client_info):
    client_info['socket'].send('Hello!\n')
    recv_buffer = client_info['socket'].recv(1024)
    print "From %s: %s" % (client_info['ip'], recv_buffer )
    client_info['socket'].send('Shut Down!\n')

    #关闭客户端
    client_info['socket'].close()

if __name__ == '__main__':
    server_scoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_scoket.bind((bind_ip, bind_port))
    server_scoket.listen(5)
    print 'Server start, listening on %s:%d' % (bind_ip, bind_port)


    while(True):
        client_socket, client_addr = server_scoket.accept()
        print 'Connecting from %s:%d' % (client_addr[0], client_addr[1])

        client_info = {'socket':client_socket, 'ip':client_addr[0]}
        #多线程
        client_thread = threading.Thread(target=client_process, args=(client_info,))
        client_thread.start()
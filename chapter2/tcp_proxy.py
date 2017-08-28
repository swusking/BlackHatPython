#!/usr/bin/env python
#coding:utf-8
'''
local开启服务器端模式，服务器端开启后，再开启客户端模式
remote开启客户端模式
python tcp_proxy.py 127.0.0.1 110 pop3.swu.edu.cn 110
'''
import sys, socket, threading

def hexdump(str, length=16):
    result = ''
    digits = 4 if isinstance(str, unicode) else 2

    for i in xrange(0, len(str), length):
        s = str[i:length+i]
        hex_str = ' '.join([ '%0*X' % (digits, ord(x)) for x in s])
        text_str = ''.join([ x if chr(32)<x<chr(127) else '.' for x in s])
        line_str = '%04X  %-*s  %s' %(i, length*(1+digits),hex_str, text_str)
        result = result + line_str + '\n'

    return result


def recv_from(socket):
    recv_buffer = ''
    socket.settimeout(5)
    #超时会报错，所以抛出异常
    try:
        while True:
            temp = socket.recv(1024)
            if not temp:
                break
            recv_buffer = recv_buffer + temp
    except:
        pass

    return recv_buffer

def server_loop(server_socket, client_socket):

    while True:
        client_recv_buffer = recv_from(client_socket)
        if client_recv_buffer:
            print '[<===]Recived %d from localhost' % len(client_recv_buffer)
            print hexdump(client_recv_buffer)
            server_socket.send(client_recv_buffer)

        server_recv_buffer = recv_from(server_socket)
        if server_recv_buffer:
            print '[<===]Recived %d from remote' % len(server_recv_buffer)
            print hexdump(server_recv_buffer)
            client_socket.send(server_recv_buffer)

        if not client_recv_buffer or not server_recv_buffer:
            client_socket.close()
            server_socket.close()
            print 'Timeout, closed'
            break


#本地服务器端处理连入客户端进程
def client_process(client_socket, remote_ip, remote_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((remote_ip, remote_port))
    except:
        print 'Failed to connect %s:%d' % (remote_ip, remote_port)

    print 'Sucessfully connect to %s:%d' % (remote_ip, remote_port)

    #如果对方要发送banner，则接受。我们接受的时候设置timeout
    server_recv_buffer = recv_from(server_socket)
    if server_recv_buffer:
        print '[<===]Recived from remote %s:%d' % (remote_ip, remote_port)
        print hexdump(server_recv_buffer)
        client_socket.send(server_recv_buffer)

    #开始循环，收-处理-发
    server_loop(server_socket, client_socket)


#本地开启服务器端
def server_start(local_ip, local_port, remote_ip, remote_port):
    try:
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.bind((local_ip, local_port))
        local_socket.listen(5)
    except:
        print 'Faild listen on %s:%d' % (local_ip, local_port)
        sys.exit(0)

    print 'Listening on %s:%d' % (local_ip, local_port)
    #本地服务器开启成功
    while(True):
        #如果有客户端连入
        client_socket, addr = local_socket.accept()
        client_socket.send('This is sking TCP PROXY.....\n')
        print '[===>]Recive connection from %s:%d' % (addr[0], addr[1])
        client_thread = threading.Thread(target=client_process, args=(client_socket, remote_ip, remote_port))
        client_thread.start()


#比较参数是否正确
def main():
    if len(sys.argv[1:]) != 4:
        print 'Usage: ./tcp_proxy.py local_ip local_port remote_ip remote_port'
        print 'Example: ./tcp_proxy.py 127.0.0.1 110 pop3.swu.edu.cn 110'

    local_ip = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_ip = sys.argv[3]
    remote_port = int(sys.argv[4])

    server_start(local_ip, local_port, remote_ip, remote_port)


if __name__ == '__main__':
    main()
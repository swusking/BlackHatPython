#!/usr/bin/env python
#coding:utf-8
'''
模拟了一个SSH服务器功能，支持用户名密码认证
RSA的密钥没有保存在文件，是实时生成的
'''
import socket, sys, threading
import paramiko

#配置RSA文件
#host_key = paramiko.RSAKey(filename='test.rsa.key')
host_key = paramiko.RSAKey.generate(2048)  # 生成2048bit的SSH RSA公钥，不然无法运行

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'sking') and (password == 'yangjinxin'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

#服务器处理客户端的程序
def client_process(client_socket):
    client_session = paramiko.Transport(client_socket)
    client_session.add_server_key(host_key)
    server = Server()
    try:
        client_session.start_server(server=server)
    except paramiko.SSHException, e:
        print '[-] SSH failed'

    channel = client_session.accept(20)
    print '[+] Authenticated!'
    channel.send('Welcome to Sking SSH')   #发送banner信息给客户端
    while(True):
        command = raw_input('[SSH #] ')
        channel.send(command)
        print channel.recv(1024)

def main(bind_ip, bind_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #如果两次执行改程序的操作时间过短，因为timeout的设置，资源被占用不可用，设置这个可解决这个问题
        server_socket.bind((bind_ip, bind_port))
        server_socket.listen(5)
        print '[+] listening for connection...'

        while True:
            client_socket, addr = server_socket.accept()
            print '[+] Connected From: %s:%d' % (addr[0], addr[1])
            client_thread = threading.Thread(target=client_process, args=(client_socket,))
            client_thread.start()

    except BaseException, e:
        print '[-] SERVER_SOCKET ERROR: ', e
        sys.exit()

if __name__ == '__main__':
    bind_ip = '127.0.0.1'
    bind_port = 22
    main(bind_ip, bind_port)
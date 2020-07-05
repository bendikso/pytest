from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread


"""
SERVER Handling.
"""
HEADER = 32
PORT = 5050
# socket.gethostbyname(socket.gethostname()), '0.0.0.0'
SERVER = '0.0.0.0'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!D'
message_log = []

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDR)
client_sockets = []
public_keys = []
exchanged = False


def start_server():
    server.listen(4)
    print('[SERVER RUNNING]')
    print(socket.gethostbyname(socket.gethostname()))
    while True:
        client_socket, address = server.accept()
        client_sockets.append(client_socket)
        print(f'{address} connected.')
        public_keys.append(client_socket.recv(4096).decode(FORMAT))
        client_thread = Thread(target=handle_client,
                               args=(client_socket, address))
        client_thread.start()


def handle_client(client_socket, address):
    global exchanged
    connected = True
    while connected:
        if len(client_sockets) == 2 and not exchanged:
            for socket in client_sockets:
                if client_sockets.index(socket) == 0:
                    socket.send(str(public_keys[1]).encode(FORMAT))
                else:
                    socket.send(str(public_keys[0]).encode(FORMAT))
            exchanged = True
        msg_length = client_socket.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = client_socket.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                exchanged = False
                update_clients(client_socket, address, msg)
            else:
                update_clients(client_socket, address, str(msg))
    print(f'{address} disconnected.')
    del public_keys[client_sockets.index(client_socket)]
    client_sockets.remove(client_socket)
    client_socket.close()


def update_clients(client_socket, address, msg):
    if len(client_sockets) != 0:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        for socket in client_sockets:
            socket.send(send_length)
            socket.send(message)


print('[Starting server]')
start_server()

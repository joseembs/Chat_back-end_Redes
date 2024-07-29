import socket
import threading

import app

clients = {}

def handle_client(client_socket, addr):
    buffer = ""
    while True:
        try:
            info = client_socket.recv(1024).decode("utf-8")
            print("aqui1")

            if not info:
                remove_client(client_socket, addr)
                break
            print("aqui2")

            buffer += info

            while '\n' in buffer:
                print("aqui3")
                message, buffer = buffer.split('\n', 1) # para detectar o fim de cada mensagem

                response = app.getJson(message)

                client_socket.send((response + '\n').encode("utf-8"))
            else:
                print("aqui4")
                remove_client(client_socket, addr)
                break
        except:
            print("aqui5")
            remove_client(client_socket, addr)
            break

def broadcast(message, sender_addr):
    for client_socket, addr in clients.items():
        if addr != sender_addr:
            try:
                client_socket.send(f"{message}".encode('utf-8'))
            except:
                remove_client(client_socket, addr)

def remove_client(client_socket, addr):
    if client_socket in clients:
        client_socket.close()
        del clients[client_socket]
        print(f"Conexão com {addr} fechada")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("Servidor iniciado e aguardando conexões...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")
        clients[client_socket] = addr
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    main()
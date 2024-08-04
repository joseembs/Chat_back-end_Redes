import socket
import threading

import app

clients = {}

def handle_client(client_socket, addr):
    buffer = ""
    while True:
        try:
            info = client_socket.recv(1024).decode("utf-8")

            if not info:
                remove_client(client_socket, addr)
                break

            buffer += info

            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1) # para detectar o fim de cada mensagem
                print(message)

                response = app.getJson(message, client_socket)
                print(response)

                client_socket.send((response + '\n').encode("utf-8"))
            else:
                remove_client(client_socket, addr)
                break
        except:
            remove_client(client_socket, addr)
            break

def recebe_arquivo(client_socket, filename):
    try:
        print("Começa a baixar " + filename)
        with open(filename, 'wb') as f:
            a = 0
            while True:
                a += 1
                print(a)
                data = client_socket.recv(1024)
                if not data:
                    print("b")
                    break
                f.write(data)
        print(f"Arquivo {filename} recebido com sucesso.")
        remove_client(client_socket, addr)

    
    except:
        print(f"Ocorreu um erro")
        remove_client(client_socket, addr)
        break

def envia_arquivo(client_socket, filename):
    try:
        with open(filename, 'rb') as f:
            client_socket.sendfile(f)
        print(f"Arquivo {filename} enviado de volta com sucesso.")
        remove_client(client_socket, addr)
    except:
        print(f"Ocorreu um erro")
        remove_client(client_socket, addr)
        break



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

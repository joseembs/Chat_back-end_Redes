import socket
import threading

import api

ip = '26.212.49.229';

def handle_client(client_socket, addr):
    buffer = ""
    try:
        info = client_socket.recv(1024).decode("utf-8")

        if not info:
            remove_client(client_socket, addr)
        else:
            buffer += info

            if '\n' in buffer:
                message, buffer = buffer.split('\n', 1) # para detectar o fim de cada mensagem
                print(message)

                response = app.getJson(message, client_socket, addr)
                print(response)

                client_socket.send((response + '\n').encode("utf-8"))
                remove_client(client_socket, addr)
            else:
                remove_client(client_socket, addr)

    except:
        remove_client(client_socket, addr)


def recebe_arquivo(client_socket, addr, filename):
    try:
        print("Começa a baixar " + filename)
        with open(filename, 'wb') as f:
            a = 0
            while True:
                a += 1
                print(a)
                data = client_socket.recv(1024)
                if not data:
                    print("end data")
                    break
                f.write(data)
        print(f"Arquivo {filename} recebido com sucesso.")
        remove_client(client_socket, addr)
    
    except:
        print(f"Ocorreu um erro")
        remove_client(client_socket, addr)

def envia_arquivo(client_socket, addr, filename):
    try:
        with open(filename, 'rb') as f:
            client_socket.sendfile(f)
        print(f"Arquivo {filename} enviado de volta com sucesso.")
        remove_client(client_socket, addr)
    except:
        print(f"Ocorreu um erro")
        remove_client(client_socket, addr)

def remove_client(client_socket, addr):
    print(f"Conexão com {addr} fechada")
    client_socket.close()



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('26.212.49.229', 12345))
    server.listen(5)
    print("Servidor iniciado e aguardando conexões...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    main()
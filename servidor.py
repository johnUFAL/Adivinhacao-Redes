# Servidor python

import socket 
import threading
import random
#from protocolo import Protocolo

#Inicar server, inicar jogo, notificar, remover desconectados, receber dados, criar thread 

#multiplos clientes
def clientes(conexao, endereco):
    print(f'[Nova conexão] cliente conectado em {endereco}')

    while True:
        try:
            msg = conexao.recv(1024).decode()
            if not msg:
                break
            print(f'[{endereco}]: {msg}')
            conexao.send(f'servidor recebeu: {msg}'.encode())
        except:
            break

    print(f'[desconectado] {endereco}')
    conexao.close()

def main():
    # cria socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind em 8888
    servidor.bind(('localhost', 8888))
    #agaurda conexão
    servidor.listen()
    print('[server ativado]')

    while True:
        conexao, endereco = servidor.accept()
        thread = threading.Thread(target=clientes, args=(conexao, endereco))
        thread.start()
        print(f'[conexoes ativas] {threading.active_count() - 1}')


if __name__ == '__main__':
    main()
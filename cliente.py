#conectar, escutar, enviar, inicar cliente, inicar thread 
import socket
import threading
import time
from protocolo import Protocolo


#thread para ouvir server
def ouvir_server(cliente):
    while True:
        try:
            resp = cliente.recv(1024).decode()
            if not resp:
                break
            comando, dados = Protocolo.decodificar(resp)
            print(f'SERVER: {comando} | {dados}')

        except:
            break

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('localhost', 8888))

#iniciar threads
thread = threading.Thread(target=ouvir_server, args=(cliente,))
thread.daemon = True
thread.start()

while True:
    tentativa = input('Escolha um número ou sair: ')
    if tentativa.lower() == 'sair':
        time.sleep(.2)
        cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode())
        break
    
    time.sleep(.2)
    cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode())

cliente.close()
#conectar, escutar, enviar, inicar cliente, inicar thread 
import socket
import threading
import time
from protocolo import Protocolo

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('localhost', 8888))

while True:
    tentativa = input('Num ou sair: ')
    if tentativa.lower() == 'sair':
        time.sleep(.2)
        cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode())
        break
    
    time.sleep(.2)
    cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode())
    
    resp = cliente.recv(1024).decode()
    if not resp:
        print('Server fechado.')
        break
    
    comando, dados = Protocolo.decodificar(resp)
    print(f'Server resposta: {comando} | {dados}')

cliente.close()
# Cliente python
import socket
import threading
import time
from protocolo import Protocolo

#conectar, escutar, enviar, inicar cliente, inicar thread 
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('localhost', 8888))

mensagem = Protocolo.codificar(Protocolo.TENTATIVA, "10")
cliente.send(mensagem.encode())

resp = cliente.recv(1024).decode()
comando, dados = Protocolo.decodificar(resp)
print(f'Server resposta: {comando} | {dados}')

cliente.close()
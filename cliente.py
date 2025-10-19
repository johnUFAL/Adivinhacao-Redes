# Cliente python
import socket
import threading
import time
#from protocolo import Protocolo

#conectar, escutar, enviar, inicar cliente, inicar thread 

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('localhost', 8888))
mensagem = input()
cliente.send(mensagem.encode())

cliente.close()
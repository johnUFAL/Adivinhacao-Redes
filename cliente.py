#conectar, escutar, enviar, inicar cliente, inicar thread 
import socket
import threading
import time
from protocolo import Protocolo

LOCALHOST = "localhost" # em que host irá operar
PORTA = 8888 # em que porta irá operar

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o objeto socket
# socket.AF_INET = rede IPV4
# socket.SOCK_STREAM = protocolo TCP

cliente.connect((LOCALHOST, PORTA)) # se conecta ao servidor

print("Adivinhe o numero escolhido entre 1 e 100 [-1 para sair]: ") # texto inicial

while True:

    tentativa = int(input('Valor: ')) # será perguntado indefinidamente

    if tentativa == -1:
        time.sleep(.2)
        cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode()) # envia uma mensagem de saida para o servidor
        resp = cliente.recv(1024).decode() # recebe a mensagem de saida do servidor mostrando que ele recebeu a solicitação de saida
        comando, dados = Protocolo.decodificar(resp)

        if comando == Protocolo.FIM_PARTIDA:
            print(f'Server resposta: {comando} | {dados}')
        else:
            print("Erro ao se desconectar! Você ainda está conectado")
            continue

        break
    
    time.sleep(.2)
    cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode()) # envia uma mensagem com a tentativa para o servidor
    
    resp = cliente.recv(1024).decode() # recebe uma mensagem do servidor com até 1024 bytes que será transformada de bytes para string

    if not resp:
        print('Server fechado.')
        break
    
    # caso não esteja vazia, essa mensagem que já foi transformada será dividida em (comando, dados)
    comando, dados = Protocolo.decodificar(resp)
    # print(f'Server resposta: {comando} | {dados}')

    if comando == Protocolo.ERRO:
        print("Você digitou um valor inválido!")
    elif comando == Protocolo.ACERTOU:
        print(f"{dados}")
        continue
    else: # MAIOR ou MENOR
        print(f'Dica: {dados}')
        continue

cliente.close() # se desconecta do servidor
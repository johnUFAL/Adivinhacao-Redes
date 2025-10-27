#conectar, escutar, enviar, inicar cliente, inicar thread 
import socket
import threading
import time
import sys
from protocolo import Protocolo

LOCALHOST = "localhost" # em que host irá operar
PORTA = 8888 # em que porta irá operar
rodando = True # variavel global de controle para caso o servidor se desconecte
aguardar = False # variavel global de controle para caso o cliente vença

def recebe_servidor(cliente):
    global rodando
    global aguardar

    while rodando:
        resp = cliente.recv(1024).decode() # recebe uma mensagem do servidor com até 1024 bytes que será transformada de bytes para string

        if not resp:
            print("Server fechado =(")
            break

        mensagens = resp.split("\n") # para caso seja recebida multiplas mensagens do servidor

        for msg in mensagens:
            if not msg:
                continue

            # caso não esteja vazia, essa mensagem que já foi transformada será dividida em (comando, dados)
            comando, dados = Protocolo.decodificar(msg)
            # print(f'Server resposta: {comando} | {dados}')

            if comando == Protocolo.ERRO:
                print(dados)
            elif comando == Protocolo.FIM_PARTIDA:
                print(dados)
                rodando = False
                # cliente.close()
                # sys.exit(0)
            elif comando == Protocolo.FIM_SERVIDOR:
                print(dados)
                rodando = False
                # cliente.close()
                # sys.exit(0)
            elif comando == Protocolo.ACERTOU:
                print(dados)
                aguardar = True
            elif comando == Protocolo.AVISO:
                print(dados)
            else: # MAIOR ou MENOR
                print(f'Dica: {dados}')
        
def envio_mensagem(cliente):
    print("Adivinhe o numero escolhido entre 1 e 100 [-1 para sair]: ") # texto inicial

    global rodando
    global aguardar

    while rodando:

        if not aguardar: # para impedir o usuario de inputar algo ao vencer

            try:
                tentativa = int(input('Valor: ')) # será perguntado indefinidamente
            except:
                print("Valor invalido")
                continue

            if tentativa == -1:
                try:
                    cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode()) # envia uma mensagem de saida para o servidor
                    time.sleep(.2)
                    cliente.close()
                    continue
                except (ConnectionResetError, BrokenPipeError): 
                    print("Server fechado =(")
                    # ConnectionResetError → servidor fechou a conexão abruptamente
                    # BrokenPipeError → ocorre quando se tenta escrever em socket fechado

            try:
                cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode()) # envia uma mensagem com a tentativa para o servidor
                time.sleep(.2)
            except (ConnectionResetError, BrokenPipeError): 
                print("Server fechado =(")

####################
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o objeto socket
# socket.AF_INET = rede IPV4
# socket.SOCK_STREAM = protocolo TCP

try:
    cliente.connect((LOCALHOST, PORTA)) # se conecta ao servidor
except:
    print("Servidor indisponivel")
    sys.exit(0)

thread_recebe = threading.Thread(target=recebe_servidor, args=(cliente,))
thread_recebe.start()
thread_envio = threading.Thread(target=envio_mensagem, args=(cliente,))
thread_envio.start()
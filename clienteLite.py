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
            print("Server fechado =( 3")
            break

        mensagens = resp.split("\n") # para caso seja recebida multiplas mensagens do servidor

        for msg in mensagens:
            if not msg:
                continue

            # caso não esteja vazia, essa mensagem que já foi transformada será dividida em (comando, dados)
            comando, dados = Protocolo.decodificar(msg)
            # print(f'Server resposta: {comando} | {dados}')

            if comando == Protocolo.ERRO: # para valores ou comandos errados que por acaso passaram do tratamento de erros nesse arquivo
                print(dados)
            elif comando == Protocolo.NEXT: # proximo level
                print(dados)
                aguardar = False # todos poderão digitar agora
            elif comando == Protocolo.FIM_PARTIDA: # jogador saiu da partida
                print(dados)
                rodando = False # irá cancelar os loops infinitos das threads
                # cliente.close()
                # sys.exit(0)
            elif comando == Protocolo.FIM_SERVIDOR: # servidor desconectou
                if aguardar: # para caso o usuario esteja aguardando os outros jogadores acertarem
                    print(dados)
                else:
                    print(f"[Skip]\n{dados}") # gambiarra no prompt para os jogadores que ainda não acertaram
                # print(dados)
                rodando = False
                # cliente.close()
                # sys.exit(0)
            elif comando == Protocolo.PERDENDO: # mensagem para os que ainda não acertaram
                print(f"{dados}\nValor: ", end="") # gambiarra no prompt
            elif comando == Protocolo.ACERTOU: # caso o jogador acerte ele ficará inapto a digitar qualquer coisa
            # mas é valido dizer que caso continue digitando no terminal estes valores irão ser armazenados no buffer de entrada
            # e posteriormente irão ser entregues ao input (funcao bloqueante)  
                print(dados)
                aguardar = True
            elif comando == Protocolo.AVISO: # aviso para os jogadores
                if aguardar:    
                    print(dados)
                else:
                    print(f"[Skip]\n{dados}\nValor: ", end="") # gambiarra no prompt
            else: # MAIOR ou MENOR, dicas sobre o prosseguimento do game
                print(f'Dica: {dados}')

# recv e input = são funções bloqueantes
        
def envio_mensagem(cliente):
    print(f"Adivinhe o numero escolhido entre o intervalo inicial de 1 a 100. A cada partida o intervalo será acrescido de 100. Warning: [-1 para sair]\nSeu endereco = {cliente.getsockname()}") # texto inicial
    # cliente.getsockname() -> Isso retorna uma tupla (ip_local, porta_local)

    global rodando
    global aguardar

    while rodando:

        if not aguardar: # para impedir o usuario de inputar algo ao vencer

            try:
                time.sleep(.15)
                tentativa = int(input('Valor: ')) # será perguntado indefinidamente
            except:
                if rodando: # gambiarra para não printar quando o servidor for desconectado
                    print("Valor invalido")
                continue

            if tentativa == -1:
                try:
                    cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode()) # envia uma mensagem de saida para o servidor
                    time.sleep(.2)
                    cliente.close()
                    continue
                except (ConnectionResetError, BrokenPipeError): 
                    print("Server fechado =( 1")
                    # ConnectionResetError → servidor fechou a conexão abruptamente
                    # BrokenPipeError → ocorre quando se tenta escrever em socket fechado

            try:
                cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode()) # envia uma mensagem com a tentativa para o servidor
                time.sleep(.2)
            except (ConnectionResetError, BrokenPipeError): 
                print("Server fechado =( 2")

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
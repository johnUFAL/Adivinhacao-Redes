import socket
import threading
from protocolo import Protocolo

LOCALHOST = "localhost" # em que host irá operar
PORTA = 8888 # em que porta irá operar

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o objeto socket
# socket.AF_INET = rede IPV4
# socket.SOCK_STREAM = protocolo TCP

cliente.connect((LOCALHOST, PORTA)) # se conecta ao servidor

# Flag para controlar encerramento
rodando = True

def receber_mensagens():
    global rodando
    while rodando:
        try:
            resp = cliente.recv(1024).decode() # recebe a mensagem de saida do servidor mostrando que ele recebeu a solicitação de saida

            if not resp:
                print("Servidor fechou a conexão.")
                rodando = False
                break

            mensagens = resp.split("\n") # para caso seja recebida multiplas mensagens do servidor

            for msg in mensagens:
                if not msg:
                    continue

                comando, dados = Protocolo.decodificar(msg) # caso não esteja vazia, essa mensagem que já foi transformada será dividida em (comando, dados)
                # print(dados)

                if comando == Protocolo.FIM_PARTIDA:
                    print(f'Server resposta: {comando} | {dados}')
                    rodando = False
                    break
                elif comando == Protocolo.ERRO:
                    print("Você digitou um valor inválido!")
                elif comando == Protocolo.ACERTOU:
                    print(f"{dados}")
                    rodando = False
                elif comando == Protocolo.AVISO:
                    print(f"{dados}")
                elif comando in (Protocolo.MAIOR, Protocolo.MENOR): # MAIOR ou MENOR
                    print(f'Dica: {dados}')
                

        except Exception as e:
            print(f"[Erro recv] {e}")
            rodando = False
            break

# Inicia thread de recepção
thread_recv = threading.Thread(target=receber_mensagens, daemon=True) # daemon = thread de segundo plano
thread_recv.start()

print("Adivinhe o número entre 1 e 100 [-1 para sair]: ")  # texto inicial

# Thread principal para input do usuário
while rodando:
    try:
        entrada = input("Valor: ") # será perguntado indefinidamente
        try: # checagem validade do valor
            tentativa = int(entrada)
        except ValueError:
            print("Digite um número válido!")
            continue

        if tentativa == -1:
            cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode())
            rodando = False
            break

        cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode())  # envia uma mensagem com a tentativa para o servidor

    except KeyboardInterrupt:
        rodando = False
        break

cliente.close()
print("Conexão encerrada.")
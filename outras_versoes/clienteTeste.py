import socket
import threading
import time
from protocolo import Protocolo

LOCALHOST = "localhost"
PORTA = 8888

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((LOCALHOST, PORTA))
cliente.settimeout(0.5)  # Timeout para operações de socket

print("Adivinhe o numero escolhido entre 1 e 100 [-1 para sair]: ")
aguardar = False

while True:
    if not aguardar:
        try:
            entrada = input('Valor: ')
            tentativa = int(entrada)
        except ValueError:
            print("Erro: Digite apenas números!")
            continue

        if tentativa == -1:
            time.sleep(.2)
            try:
                cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode())
                resp = cliente.recv(1024).decode()
                comando, dados = Protocolo.decodificar(resp)

                if comando == Protocolo.FIM_PARTIDA:
                    print(f'Server resposta: {comando} | {dados}')
                else:
                    print("Erro ao se desconectar! Você ainda está conectado")
                    continue
                break
            except (BrokenPipeError, ConnectionResetError):
                print("Servidor desconectou!")
                break
        
        time.sleep(.2)
        try:
            cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode())
        except (BrokenPipeError, ConnectionResetError):
            print("Erro: Servidor desconectou!")
            break
        
        try:
            resp = cliente.recv(1024).decode()
            
            if not resp:
                print("Server fechado =(")
                break

            mensagens = resp.split("\n")
            for msg in mensagens:
                if not msg:
                    continue

                comando, dados = Protocolo.decodificar(msg)

                if comando == Protocolo.ERRO:
                    print("Você digitou um valor inválido!")
                elif comando == Protocolo.ACERTOU:
                    print(f"{dados}")
                    aguardar = True
                elif comando == Protocolo.AVISO:
                    print(f"{dados}")
                    # VERIFICA SE PODE VOLTAR A JOGAR
                    if "novo jogo" in dados.lower():
                        aguardar = False
                        print("→ Novo jogo! Você pode tentar novamente.")
                else: # MAIOR ou MENOR
                    print(f'Dica: {dados}')
                    
        except socket.timeout:
            print("Timeout: Servidor não respondeu")
            break
        except (BrokenPipeError, ConnectionResetError):
            print("Servidor desconectou!")
            break
            
    else: # Modo de espera (já acertou)
        try:
            resp = cliente.recv(1024).decode()
            
            if not resp:
                continue

            mensagens = resp.split("\n")
            for msg in mensagens:
                if not msg:
                    continue
                comando, dados = Protocolo.decodificar(msg)
                print(f"{dados}")
                
                # DETECTA REINÍCIO DO JOGO
                if "novo jogo" in dados.lower() or "reinici" in dados.lower():
                    aguardar = False
                    print("→ Novo jogo iniciado! Você pode tentar novamente.")
                    print("Adivinhe o numero escolhido entre 1 e 100 [-1 para sair]: ")
                    
        except socket.timeout:
            pass  # Timeout normal em modo de espera
        except (BrokenPipeError, ConnectionResetError):
            print("Servidor desconectou!")
            break

cliente.close()
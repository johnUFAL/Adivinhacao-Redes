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

            #mehlorando mensagens 
            if comando == Protocolo.ACERTOU:
                print(f'\n ✔ {dados}')
                print("=" * 20)

            elif comando == Protocolo.FIM_PARTIDA:
                print(f'\n 🏆 {dados}')
                print("=" * 20)

            elif comando == Protocolo.INICIAR:
                if "Segundos" in dados or "em" in dados:
                    print(f'⏳´{dados}')
                else:
                    print(f'\n NOVO JOGO INICIADO!')
                    print(f'{dados}')
                    print("=" * 20)

            elif comando == Protocolo.MAIOR:
                print(f'📈 {dados}')

            elif comando == Protocolo.MENOR:
                print(f'📉 {dados}')

            elif comando == Protocolo.ERRO:
                print(f'❌ {dados}')

            else: 
                print(f'{dados}')

        except:
            break

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('localhost', 8888))

#iniciar threads
thread = threading.Thread(target=ouvir_server, args=(cliente,))
thread.daemon = True
thread.start()

while True:
    tentativa = input('\nDigite um número ou "sair": ')
    if tentativa.lower() == 'sair':
        time.sleep(.2)
        cliente.send(Protocolo.codificar(Protocolo.SAIR, "").encode())
        break
    
    time.sleep(.2)
    cliente.send(Protocolo.codificar(Protocolo.TENTATIVA, tentativa).encode())

cliente.close()
# Servidor python
import socket 
import threading
import random
from protocolo import Protocolo

#Inicar server, inicar jogo, notificar, remover desconectados, receber dados, criar thread 
#multiplos clientes
def clientes(conexao, endereco):
    print(f'[Nova conexão] cliente conectado em {endereco}')

    num_secreto = random.randint(1, 100)
    conexao.send(Protocolo.codificar(Protocolo.INICIAR, "Adivinhe o n. escolhido entre 1 e 100").encode())

    while True:
        try:
            msg = conexao.recv(1024).decode()
            if not msg:
                break
            
            comando, dados = Protocolo.decodificar(msg)
            if comando == Protocolo.SAIR:
                conexao.send(Protocolo.codificar(Protocolo.FIM_PARTIDA, "Saindo do jogo...").encode())
                break

            elif comando == Protocolo.TENTATIVA:
                ttv = int(dados)
                if ttv > num_secreto:
                    conexao.send(Protocolo.codificar(Protocolo.MAIOR, "O numero é menor").encode())
                elif ttv < num_secreto:
                    conexao.send(Protocolo.codificar(Protocolo.MENOR, "O numero é maior").encode())
                else:
                    conexao.send(Protocolo.codificar(Protocolo.ACERTOU, "Voceê acertou!!!").encode())
                    break
            else:
                conexao.send(Protocolo.codificar(Protocolo.ERRO, "Comando inválido").encode())
        
        except Exception as e:
            print(f"[Erro] {e}")
            break

    print(f'[desconectado] {endereco}')
    conexao.close()

def main():
    # cria socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind em 8888
    servidor.bind(('localhost', 8888))
    #agaurda conexão
    servidor.listen()
    print('[server ativado]')

    while True:
        conexao, endereco = servidor.accept()
        thread = threading.Thread(target=clientes, args=(conexao, endereco))
        thread.start()
        print(f'[conexoes ativas] {threading.active_count() - 1}')


if __name__ == '__main__':
    main()
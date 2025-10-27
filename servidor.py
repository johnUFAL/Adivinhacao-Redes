#Inicar server, inicar jogo, notificar, remover desconectados, receber dados, criar thread 
import socket 
import threading
import random
import time
from protocolo import Protocolo

# prpriedades do jogo e inicalização de partida
class Jogo:
    def __init__(self):
        self.num_secreto = None
        self.jogo_ativo = False
        self.clientes = [] #lita de clientes
        self.placar = {} #endreço, pontuação

    def inicar_game(self):
        self.num_secreto = random.randint(1, 100) #gerando numero aleatorio
        self.jogo_ativo = True
        print(f'Nova partida, Num: {self.num_secreto}')

    #broadcast para notificr todos
    def broadcast(self, msg, cliente_origem=None):
        cliente_remover = []
        for cliente in self.clientes:
            if cliente != cliente_origem:
                try:
                    cliente.send(msg.encode())
                except:
                    cliente_remover.append(cliente)
        
        #removendo
        for cliente in cliente_remover:
            jogo.clientes.remove(cliente)


#global game aqui
jogo = Jogo()

#multiplos clientes
def clientes(conexao, endereco):
    jogo.clientes.append(conexao)
    
    print(f'[Nova conexão] cliente conectado em {endereco}')

    time.sleep(0.2)  
    conexao.send(Protocolo.codificar(Protocolo.INICIAR, "Adivinhe o n. escolhido entre 1 e 100").encode())

    while True:
        try:
            msg = conexao.recv(1024).decode()
            if not msg:
                break
            
            comando, dados = Protocolo.decodificar(msg)
            if comando == Protocolo.SAIR:
                time.sleep(0.2)  
                conexao.send(Protocolo.codificar(Protocolo.FIM_PARTIDA, "Saindo do jogo...").encode())
                break

            elif comando == Protocolo.TENTATIVA:
                tentativa = int(dados)
                if tentativa > jogo.num_secreto:
                    time.sleep(0.2)  
                    conexao.send(Protocolo.codificar(Protocolo.MAIOR, "O numero é menor").encode())
                elif tentativa < jogo.num_secreto:
                    time.sleep(0.2)  
                    conexao.send(Protocolo.codificar(Protocolo.MENOR, "O numero é maior").encode())
                else:
                    #add broadcast
                    time.sleep(0.2)  
                    conexao.send(Protocolo.codificar(Protocolo.ACERTOU, "Voceê acertou!!!").encode())
                    
                    msg_broad = Protocolo.codificar(Protocolo.FIM_PARTIDA, f'Cliebte {endereco} acertou o número {jogo.num_secreto}!')
                    jogo.broadcast(msg_broad, conexao)
                    print(f'Cliente {endereco} acertou {jogo.num_secreto}! Notificando todos!!!')
            
                    #reinicia partida
                    jogo.inicar_game()
                    msg_new_game = Protocolo.codificar(Protocolo.INICIAR, f"Novo Jogo¹ Adivinhe o número netre 1 e 100")
            else:
                time.sleep(0.2)  
                conexao.send(Protocolo.codificar(Protocolo.ERRO, "Comando inválido").encode())
        
        except Exception as e:
            print(f"[Erro] {e}")
            break

        #pra remover cliente quando sair 
        if conexao in jogo.clientes:
            jogo.clientes.remove(conexao)

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

    jogo.inicar_game()

    while True:
        conexao, endereco = servidor.accept()
        thread = threading.Thread(target=clientes, args=(conexao, endereco))
        thread.start()
        print(f'[conexoes ativas] {threading.active_count() - 1}')


if __name__ == '__main__':
    main()
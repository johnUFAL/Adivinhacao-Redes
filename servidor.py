#Inicar server, inicar jogo, notificar, remover desconectados, receber dados, criar thread 
import socket 
import threading
import random
import time
from protocolo import Protocolo

LOCALHOST = "localhost"
PORTA = 8888

# propriedades do jogo e inicalização de partida
class Jogo:
    def __init__(self):
        self.num_secreto = None
        self.jogo_ativo = False
        self.clientes = [] #lista de clientes
        self.clientesWin = [] # lista de clientes que acertaram
        self.lock = threading.Lock() # impede com que multiplas threads executem ações que possam resultar em conflito

    def iniciar_game(self):
        self.num_secreto = random.randint(1, 100) #gerando numero aleatorio
        self.jogo_ativo = True
        print(f'Nova partida, Num: {self.num_secreto}')

    def adicionar_cliente(self, conexao):
        with self.lock:
            if conexao not in self.clientes:
                self.clientes.append(conexao)   

    def remover_cliente(self, conexao):
        with self.lock:
            if conexao in self.clientes:
                self.clientes.remove(conexao) 
            if conexao in self.clientesWin:
                self.clientesWin.remove(conexao)       

    def cliente_acertou(self, conexao):
        with self.lock:
            if conexao in self.clientes and conexao not in self.clientesWin:
                self.clientesWin.append(conexao)

    def broadcast(self, endereco):
        with self.lock:
            clientes_copy = self.clientes[:]
            clientesWin_copy = self.clientesWin[:]

        for conexao in clientes_copy:
            conexao.send((Protocolo.codificar(Protocolo.AVISO, f"Há {len(clientes_copy) - len(clientesWin_copy)} ainda jogando") + "\n").encode())

            if conexao not in clientesWin_copy:
                conexao.send((Protocolo.codificar(Protocolo.AVISO, f"Bora betinha agiliza! O colega de endereço {endereco} acertou!!!") + "\n").encode())

#global game aqui
jogo = Jogo()

#multiplos clientes
def clientes(conexao, endereco): # (socket desse novo cliente, endereço=(ip, porta))
    print(f'[Nova conexão] cliente conectado em {endereco}')
    jogo.adicionar_cliente(conexao)

    while True:
        try:
            msg = conexao.recv(1024).decode()
            # recv = lê até 1024 bytes
            # decode = transforma os bytes em string
            if not msg: 
                jogo.remover_cliente(conexao)
                break # desconecta

            comando, dados = Protocolo.decodificar(msg) # separa em comando e dados a mensagem 

            try:
                tentativa = int(dados)
            except ValueError:
                conexao.send((Protocolo.codificar(Protocolo.ERRO, "Digite um número válido") + "\n").encode())
                # conexao.send() = envia os dados para esse socket, ou esse cliente especifico
                # Protocolo.codificar = organiza a mensagem, unindo o comando e dados de uma forma padronizada e retorna uma string
                # encode = transforma a string retornada pelo codificar em bytes para que seja possivel enviar pelo socket
                continue
            
            if comando == Protocolo.SAIR:
                # time.sleep(0.2)  
                jogo.remover_cliente(conexao)
                # time.sleep(0.2)
                conexao.send((Protocolo.codificar(Protocolo.FIM_PARTIDA, "Se desconectando do servidor...") + "\n").encode())
                break
            elif comando == Protocolo.TENTATIVA: # condicionamento do valor inserido pelo usuário
                if tentativa > jogo.num_secreto:
                    # time.sleep(0.2)  
                    conexao.send((Protocolo.codificar(Protocolo.MAIOR, "O numero é menor") + "\n").encode())
                elif tentativa < jogo.num_secreto:
                    # time.sleep(0.2)  
                    conexao.send((Protocolo.codificar(Protocolo.MENOR, "O numero é maior") + "\n").encode())
                else:
                    # time.sleep(0.2)  
                    conexao.send((Protocolo.codificar(Protocolo.ACERTOU, f"Você acertou!!! Aguarde os friends acertarem") + "\n").encode())
                    jogo.cliente_acertou(conexao)
                    # time.sleep(0.2)
                    jogo.broadcast(endereco)
            else:
                # time.sleep(0.2)  
                conexao.send(Protocolo.codificar(Protocolo.ERRO, "Comando inválido").encode())
        
        except Exception as e:
            print(f"[Erro] {e}")
            break

    print(f'[desconectado] {endereco}')
    conexao.close()

def main():
    # cria socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # (tipo de Rede, tipo de Protocolo)
    # bind em 8888
    servidor.bind((LOCALHOST, PORTA)) # associa a um endereço e porta fixas
    #aguarda conexão
    servidor.listen() # fica no modo escuta, default: 5
    print('[server ativado]')

    jogo.iniciar_game() # inicia primeira rodada

    while True: # loop para aceitar novas conexões
        conexao, endereco = servidor.accept() # cria um novo objeto socket para cada cliente
        thread = threading.Thread(target=clientes, args=(conexao, endereco))  # cria thread para atender multiplos usuarios (função que vai lidar com cada cliente, argumentos)
        thread.start() # inicia a thread
        print(f'[conexoes ativas] {threading.active_count() - 1}')

if __name__ == '__main__': # só executa diretamente
    main()
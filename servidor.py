# Iniciar server, inicar jogo, notificar, remover desconectados, receber dados, criar thread 
import socket 
import threading
import random
import time
import sys
from protocolo import Protocolo

LOCALHOST = "localhost"
PORTA = 8888

# propriedades do jogo e inicialização de partida
class Jogo:
    def __init__(self):
        self.num_secreto = None
        self.jogo_ativo = False
        self.partidas = 1 # partida number one, vai contabilizar o numero de partidas
        self.placar = {} # dicionario = {endereco: pontuacao}
        self.clientes = [] # lista de clientes
        self.clientesWin = [] # lista de clientes que acertaram
        self.lock = threading.Lock() # impede com que multiplas threads executem ações que possam resultar em conflito
        self.lock_print = threading.Lock() # impede com as threads que estão vinculadas com os clientes entrem em conflito com que recebe comandos

    def seguro_print(self, msg, apagar = False):
        with self.lock_print:
            if apagar:
                sys.stdout.write("\r" + " " * 80 + "\r")  # limpa a linha do input
            print(msg)
            if apagar:
                sys.stdout.write(msg)  # restaura o prompt
                sys.stdout.flush()
    
    def iniciar_game(self):
        self.num_secreto = random.randint(1, 100) #gerando numero aleatorio
        self.jogo_ativo = True
        # print(f'Nova partida, Num: {self.num_secreto}')
        self.seguro_print(f'Partida {self.partidas}°, Num: {self.num_secreto}')

    def proximo_level(self):
        # with self.lock:  porque já está sendo usado na função cliente_acertou        
        self.partidas += 1 # vai aumentando a dificuldade 
        self.clientesWin.clear() # limpa a lista dos vencedores
        self.num_secreto = random.randint(1, (100 * self.partidas)) # 100, 200, 300, ...
        self.seguro_print(f'Partida {self.partidas}°, Num: {self.num_secreto}')
        
        for chave in self.placar: # printa para o servidor
            msg = f"endereco={chave}, pontuacao={self.placar[chave]}"
            self.seguro_print(msg)

        for c in self.clientes: # envia uma mensagem para todos
            c.send(Protocolo.codificar(Protocolo.RESET, f"Vamos voltar com as brincadeiras gostosas, parte {self.partidas}").encode())

    def resetar_game(self):
        self.partidas = 1
        self.num_secreto = random.randint(1, 100)
        self.seguro_print(f'Retornando a partida {self.partidas}°, Num: {self.num_secreto}')

    def adicionar_cliente(self, conexao, endereco):
        with self.lock:
            if conexao not in self.clientes:
                self.clientes.append(conexao)
                self.placar[endereco] = 0 # inicializa o placar do jogador em zero   

    def remover_cliente(self, conexao, endereco):
        with self.lock:
            if conexao in self.clientes:
                self.clientes.remove(conexao) 
                self.placar.pop(endereco, None) # remove o endereco do jogador do placar
            
            if conexao in self.clientesWin:
                aviso_saida = "Um dos vencedores saiu!"
                self.clientesWin.remove(conexao) 
            else:
                aviso_saida = "Um beta saiu!"
            
            for c in self.clientes:
                conexao.send(Protocolo.codificar(Protocolo.AVISO, aviso_saida).encode())

            if len(self.clientes) == 0: # para o caso de faltar somente um jogador para completar e este sair da partida
                self.resetar_game()     

    def cliente_acertou(self, conexao, endereco):
        with self.lock:
            if conexao in self.clientes and conexao not in self.clientesWin: # caso esteja na lista de jogadores e ainda não tenha sido adicionado na lista de vencedores
                self.clientesWin.append(conexao)

                if len(self.clientesWin) == 1: # se a lista de vencedores for igual a 1, adiciona o primeiro vencedor
                    self.placar[endereco] += 1 # apenas o primeiro vencedor pontua
                    # chegando ao valor 1  
                        # pela esquerda (0 para infinito):
                            # se for esse o caso apenas o primeiro jogador irá pontuar
                        # pela direita (infinito para 0):
                            # o numero de jogadores vencedores pode diminuir, caso um dos vencedores saia e o total de vencedores fosse igual a 2, ainda sim, não ocorreria problemas, pois a funcao cliente_acertou não seria chamada e a adicao de novos jogadores vem antes da checagem

            self.broadcast(endereco) # envia mensagem da quantidade restante de jogadores que faltam e avisa para correr os que ainda não acertaram

            if len(self.clientes) > 0 and len(self.clientes) == len(self.clientesWin): # se houver jogadores e a lista de vencedores for igual a de jogadores
                self.proximo_level()

    def broadcast(self, endereco):
        # with self.lock: porque já está sendo usado na função cliente_acertou
        #     clientes_copy = self.clientes[:] # copias rasas de segurança
        #     clientesWin_copy = self.clientesWin[:] 

        clientes_copy = self.clientes[:] # copias rasas por segurança
        clientesWin_copy = self.clientesWin[:] 

        for conexao in clientes_copy:
            conexao.send((Protocolo.codificar(Protocolo.AVISO, f"Há {len(clientes_copy) - len(clientesWin_copy)} ainda jogando")).encode()) # mensagem para todos os clientes
           
            if conexao not in clientesWin_copy:
                conexao.send((Protocolo.codificar(Protocolo.PERDENDO, f"Bora betinha agiliza! O colega de endereço {endereco} acertou!!!")).encode()) # mensagem para apenas os clientes que ainda não acertaram

#global game aqui
jogo = Jogo()

#multiplos clientes
def clientes(conexao, endereco): # (socket desse novo cliente, endereço=(ip, porta))
    # print(f'[Nova conexão] cliente conectado em {endereco}')
    jogo.seguro_print(f'[Nova conexão] cliente conectado em {endereco}')
    jogo.adicionar_cliente(conexao, endereco)

    while True:
        try:
            msg = conexao.recv(1024).decode()
            # recv = lê até 1024 bytes
            # decode = transforma os bytes em string
            if not msg: 
                jogo.remover_cliente(conexao, endereco)
                break # desconecta

            comando, dados = Protocolo.decodificar(msg) # separa em comando e dados a mensagem 
            
            if comando == Protocolo.SAIR:
                jogo.remover_cliente(conexao, endereco)
                
                conexao.send((Protocolo.codificar(Protocolo.FIM_PARTIDA, "Se desconectando do servidor...")).encode())
                # conexao.send() = envia os dados para esse socket, ou esse cliente especifico
                # Protocolo.codificar = organiza a mensagem, unindo o comando e dados de uma forma padronizada e retorna uma string
                # encode = transforma a string retornada pelo codificar em bytes para que seja possivel enviar pelo socket
                break
            elif comando == Protocolo.TENTATIVA: # condicionamento do valor inserido pelo usuário
                try:
                    valor_inserido = int(dados)
                except:
                    conexao.send((Protocolo.codificar(Protocolo.ERRO, "Valor inserido inválido")).encode())
                    continue
            
                if valor_inserido > jogo.num_secreto:
                    conexao.send((Protocolo.codificar(Protocolo.MAIOR, "O numero é menor")).encode())
                elif valor_inserido < jogo.num_secreto:
                    conexao.send((Protocolo.codificar(Protocolo.MENOR, "O numero é maior")).encode())
                else:
                    if len(jogo.clientes) == 1:
                        conexao.send((Protocolo.codificar(Protocolo.ACERTOU, f"Que venha a próxima rodada!")).encode()) # mensagem para todos os clientes
                    else:
                        conexao.send((Protocolo.codificar(Protocolo.ACERTOU, "Você acertou!!! Aguarde os friends acertarem")).encode())

                    time.sleep(.1)
                    
                    jogo.cliente_acertou(conexao, endereco)
                    # jogo.broadcast(endereco)
            else:
                conexao.send(Protocolo.codificar(Protocolo.ERRO, "Comando inválido").encode())
        except Exception as e:
            # print(f"[Erro] {e}")
            jogo.seguro_print(f"[Erro] {e}")
            break

    # print(f'[desconectado] {endereco}')
    jogo.seguro_print(f'[desconectado] {endereco}')
    conexao.close()

def comando_servidor(servidor, jogo): # (conexao do servidor, objeto jogo)
    while True:

        try:
            cmd = input("").strip().upper()
            print("\r" + " " * 80 + "\r", end="")
        except:
            # print("Digito inválido")
            jogo.seguro_print("Digito inválido")
            continue 

        if cmd == "Y":
            # print("Encerrando servidor e desconectando jogadores")
            jogo.seguro_print("Encerrando servidor e desconectando jogadores...")

            with jogo.lock:
                for c in jogo.clientes:
                    try:
                        print(c)
                        c.send((Protocolo.codificar(Protocolo.FIM_SERVIDOR, "Admin encerrou o servidor. Até logo")).encode())
                        # c.close()
                    except:
                        pass

                jogo.clientes.clear()
                jogo.clientesWin.clear()

            servidor.close()
            break

def main(): # thread principal
    # cria socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # (tipo de Rede, tipo de Protocolo)
    # bind em 8888
    servidor.bind((LOCALHOST, PORTA)) # associa a um endereço e porta fixas
    # aguarda conexão
    servidor.listen() # fica no modo escuta, default: 5
    # print('[server ativado]')
    jogo.seguro_print('[server ativado]')

    jogo.iniciar_game() # inicia primeira rodada

    # thread para receber comandos
    thread_comandos = threading.Thread(target=comando_servidor, args=(servidor, jogo), daemon=True)
    thread_comandos.start()

    while True: # loop para aceitar novas conexões com uma thread para cada
        try:
            conexao, endereco = servidor.accept() # cria um novo objeto socket para cada cliente
            thread = threading.Thread(target=clientes, args=(conexao, endereco), daemon=True)  # cria thread para atender multiplos usuarios (função que vai lidar com cada cliente, argumentos)
            thread.start() # inicia a thread
            # print(f'[conexoes ativas] {threading.active_count() - 1}')
            jogo.seguro_print(f"[conexoes ativas] {threading.active_count() - 2}") # 2 = (thread principal (main)) + (thread auxiliar de leitura)
        except:
            break

if __name__ == '__main__': # só executa diretamente
    main()
# Iniciar server, iniciar jogo, notificar, remover desconectados, receber dados, criar thread 
import socket 
import threading
import random
import time
from protocolo import Protocolo

LOCALHOST = "localhost"
PORTA = 8888

class Jogo:
    def __init__(self):
        self.num_secreto = None
        self.jogo_ativo = False
        self.clientes = []  # lista de clientes
        self.clientesWin = []  # lista de clientes que acertaram
        self.lock = threading.Lock()
        self.iniciar_game()

    def _conexao_ativa(self, conexao):
        """Verifica se uma conexão ainda está ativa"""
        try:
            # Testa se a conexão ainda é válida
            conexao.getpeername()
            return True
        except:
            return False

    def iniciar_game(self):
        with self.lock:
            self.num_secreto = random.randint(1, 100)
            self.jogo_ativo = True
            self.clientesWin = []  # Limpa a lista de vencedores
            print(f'Nova partida iniciada. Clientes conectados: {len(self.clientes)}')

    def verificar_e_reiniciar_jogo(self):
        """Verifica se todos os clientes ativos acertaram e reinicia o jogo"""
        with self.lock:
            # Filtra apenas clientes com conexão ativa
            clientes_ativos = [c for c in self.clientes if self._conexao_ativa(c)]
            
            if (self.jogo_ativo and len(clientes_ativos) > 0 and 
                len(clientes_ativos) == len(self.clientesWin)):
                print(f"Todos os {len(clientes_ativos)} clientes ativos acertaram! Reiniciando jogo...")
                self.iniciar_game()
                
                # Notifica todos os clientes sobre o novo jogo
                for conexao in clientes_ativos:
                    try:
                        conexao.send((Protocolo.codificar(
                            Protocolo.AVISO, 
                            "Novo jogo iniciado! Tente adivinhar o novo número."
                        ) + "\n").encode())
                    except:
                        self.remover_cliente(conexao)

    def adicionar_cliente(self, conexao):
        with self.lock:
            if conexao not in self.clientes:
                self.clientes.append(conexao)
                print(f'Clientes totais: {len(self.clientes)}')

    def remover_cliente(self, conexao):
        with self.lock:
            if conexao in self.clientes:
                self.clientes.remove(conexao)
            if conexao in self.clientesWin:
                self.clientesWin.remove(conexao)
            print(f'Clientes restantes: {len(self.clientes)}')
            self.verificar_e_reiniciar_jogo()

    def cliente_acertou(self, conexao):
        with self.lock:
            if (conexao in self.clientes and 
                conexao not in self.clientesWin and 
                self._conexao_ativa(conexao)):
                self.clientesWin.append(conexao)
                self.verificar_e_reiniciar_jogo()

    def broadcast(self, endereco):
        """Notifica todos os clientes que alguém acertou"""
        with self.lock:
            clientes_copy = self.clientes[:]
            clientes_win_copy = self.clientesWin[:]
            count_restantes = len(clientes_copy) - len(clientes_win_copy)

        for conexao in clientes_copy:
            try:
                if conexao not in clientes_win_copy:
                    mensagem = f"Há {count_restantes} jogadores restantes. Cliente {endereco} acertou!"
                    conexao.send((Protocolo.codificar(Protocolo.AVISO, mensagem) + "\n").encode())
            except:
                # Remove cliente se não conseguir enviar
                self.remover_cliente(conexao)

# Global game instance
jogo = Jogo()

def clientes(conexao, endereco):
    print(f'[Nova conexão] Cliente conectado: {endereco}')
    jogo.adicionar_cliente(conexao)

    try:
        # Configura timeout para evitar clientes travados
        conexao.settimeout(300.0)  # 5 minutos de timeout
        
        # Mensagem de boas-vindas
        conexao.send((Protocolo.codificar(
            Protocolo.AVISO, 
            "Bem-vindo ao jogo! Adivinhe o número entre 1 e 100."
        ) + "\n").encode())
        
        while True:
            msg = conexao.recv(1024).decode().strip()
            
            if not msg: 
                print(f'[Conexão fechada] Cliente {endereco} desconectou')
                break

            comando, dados = Protocolo.decodificar(msg)

            # Verifica se o cliente já acertou
            if conexao in jogo.clientesWin:
                conexao.send((Protocolo.codificar(
                    Protocolo.AVISO, 
                    "Você já acertou! Aguarde os outros jogadores."
                ) + "\n").encode())
                continue

            # Validação de tentativa
            if comando == Protocolo.TENTATIVA:
                try:
                    tentativa = int(dados)
                except ValueError:
                    conexao.send((Protocolo.codificar(
                        Protocolo.ERRO, 
                        "Digite um número válido entre 1 e 100"
                    ) + "\n").encode())
                    continue
                
                # Processa a tentativa
                if not jogo.jogo_ativo:
                    conexao.send((Protocolo.codificar(
                        Protocolo.AVISO, 
                        "Jogo finalizado. Aguarde o próximo."
                    ) + "\n").encode())
                elif tentativa > jogo.num_secreto:
                    conexao.send((Protocolo.codificar(
                        Protocolo.MAIOR, 
                        "Tente um número menor"
                    ) + "\n").encode())
                elif tentativa < jogo.num_secreto:
                    conexao.send((Protocolo.codificar(
                        Protocolo.MENOR, 
                        "Tente um número maior"
                    ) + "\n").encode())
                else:
                    conexao.send((Protocolo.codificar(
                        Protocolo.ACERTOU, 
                        "Você acertou!!! Aguarde os outros jogadores."
                    ) + "\n").encode())
                    jogo.cliente_acertou(conexao)
                    jogo.broadcast(endereco)
                    
            elif comando == Protocolo.SAIR:
                conexao.send((Protocolo.codificar(
                    Protocolo.FIM_PARTIDA, 
                    "Conexão encerrada. Até logo!"
                ) + "\n").encode())
                break
            else:
                conexao.send((Protocolo.codificar(
                    Protocolo.ERRO, 
                    "Comando inválido"
                ) + "\n").encode())
        
    except socket.timeout:
        print(f'[Timeout] Cliente {endereco} inativo')
    except Exception as e:
        print(f'[Erro] Cliente {endereco}: {e}')
    finally:
        print(f'[Desconectado] Cliente {endereco} removido')
        jogo.remover_cliente(conexao)
        try:
            conexao.close()
        except:
            pass

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((LOCALHOST, PORTA))
    servidor.listen()
    print(f'[Servidor ativado] Escutando em {LOCALHOST}:{PORTA}')

    try:
        while True:
            conexao, endereco = servidor.accept()
            thread = threading.Thread(target=clientes, args=(conexao, endereco))
            thread.daemon = True
            thread.start()
            print(f'[Conexões ativas] {threading.active_count() - 1}')
    except KeyboardInterrupt:
        print("\n[Servidor] Encerrado pelo usuário")
    except Exception as e:
        print(f'[Erro no servidor] {e}')
    finally:
        servidor.close()
        print('[Servidor] Socket fechado')

if __name__ == '__main__':
    main()
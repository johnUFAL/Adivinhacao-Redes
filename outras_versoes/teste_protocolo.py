from protocolo import Protocolo

mensagem = Protocolo.codificar(Protocolo.ACERTOU, "Você ganhou!")
print(f'Msg codificada: {mensagem}')

comando, dados = Protocolo.decodificar(mensagem)
print(f'Comando: {comando}, Dados: {dados}')
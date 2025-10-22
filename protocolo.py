# Protocolo python: comandos e respostas

class Protocolo:
    #cliente-servidor
    TENTATIVA = "TENTATIVA"
    SAIR = "SAIR"

    #respostas do server
    INICIAR = "INICIAR"
    MAIOR = "MAIOR"
    MENOR = "MENOR"
    ACERTOU = "ACERTOU"
    FIM_PARTIDA = "FIM_PARTIDA"
    ERRO = "ERRO"

    @staticmethod
    def codificar(comando, dados=""):
        return f"{comando}|{dados}"

    @staticmethod
    def decodificar(mensagem):
        partes = mensagem.split("|", 1) #dividndo a string por cada |
        
        if len(partes) == 2:
            comando, dados = partes #decodificando
        else:
            comando, dados = partes[0], ""
        
        return comando, dados
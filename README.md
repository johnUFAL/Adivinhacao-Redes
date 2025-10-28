# Jogo de Adivinhação em Rede

Um jogo multiplayer de adivinhação onde múltiplos clientes competem para adivinhar um número secreto escolhido pelo servidor

## Funcionalidades

- Servidor TCP que gerencia o jogo
- Múltiplos clientes podem conectar simultaneamente
- Threads em cada cliente para escutar e enviar mensagens ao servidor
- Sistema de broadcast para notificar todos os clientes
- Protocolo de comunicação personalizado

## Instruções

Deverá ser aberta no mínimo duas janelas no cmd, ou prompt de comando, para a operação adequada do game. Sendo uma destinada ao servidor e a outra para o jogador, ou cliente, ficando a critério do usuário abrir mais janelas para executar o arquivo para os novos jogadores. 
No arquivo servidor.py foi adicionada uma função chamada broadcast que irá enviar para todos os clientes, ou jogadores, quantos ainda faltam acertar o número, ademais foi colocada uma condição nessa função que envia uma mensagem para todos os ainda não vencedores para eles agilizarem o raciocínio.
O placar do game é printado no arquivo do servidor e o jogo não tem um limite de level e nem de tentativas, e ele reinicia quando todos os jogadores saem.
OBS.: o jogo foi apenas testado localmente

1. **Inicie o servidor:**
   ```bash
   python servidor.py

2. **Inicie o cliente (pelo menos um para testar):**
    ```bash
    python clienteLite.py

# Jogo de Adivinhação em Rede

Um jogo multiplayer de adivinhação onde múltiplos clientes competem para adivinhar um número secreto escolhido pelo servidor.

## Funcionalidades

- Servidor TCP que gerencia o jogo
- Múltiplos clientes podem conectar simultaneamente
- Threads em cada cliente para escutar mensagens do servidor
- Sistema de broadcast para notificar todos os clientes
- Protocolo de comunicação personalizado

## Como Executar

Deverá ser aberta no mínimo três janelas no cmd, ou prompt de comando, para a operação adequada do game. Sendo uma destinada ao servidor e as outras para os jogadores, ou clientes, ficando a critério do usuário abrir mais janelas para novos jogadores

1. **Inicie o servidor:**
   ```bash
   python servidor.py

2. **Inicie o cliente (pelo menos dois):**
    ```bash
    python cliente.py
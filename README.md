# Jogo de Adivinhação em Rede

Um jogo multiplayer de adivinhação onde múltiplos clientes competem para adivinhar um número secreto escolhido pelo servidor.

## Funcionalidades

- Servidor TCP que gerencia o jogo
- Múltiplos clientes podem conectar simultaneamente
- Threads em cada cliente para escutar mensagens do servidor
- Sistema de broadcast para notificar todos os clientes
- Protocolo de comunicação personalizado

## Como Executar

1. **Inicie o servidor:**
   ```bash
   python servidor.py

2. **Inicie o cliente (pelo menos dois):**
    ```bash
    python cliente.py
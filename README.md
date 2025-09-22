# Backend - Sistema de Acesso OAB

Este é o serviço de backend em Python para a aplicação de quiosque da OAB. Ele gerencia a autenticação e a sessão dos advogados através de uma API local.

## Setup do Ambiente

1.  Certifique-se de ter o Python 3.10+ instalado.
2.  Clone este repositório ou baixe os arquivos.
3.  Abra um terminal na pasta do projeto e instale as dependências com o seguinte comando:
    ```
    pip install -r requirements.txt
    ```

## Como Iniciar o Servidor

Para iniciar o backend, execute o seguinte comando no terminal, dentro da pasta do projeto:

```
python backend.py
```

O servidor estará disponível no endereço `http://127.0.0.1:5000`. O log de eventos (tentativas de login, etc.) aparecerá nesta janela do terminal.

## Documentação da API

A comunicação entre o frontend (Electron) e o backend (Python) é feita via requisições HTTP para os seguintes endpoints.

### **1. `POST /login`**

Realiza a autenticação do advogado.

-   **URL:** `/login`
-   **Método:** `POST`
-   **Corpo da Requisição (JSON):**
    ```json
    {
      "oab": "MA12345",
      "cpf": "333.333.333-33"
    }
    ```
-   **Resposta de Sucesso (Código 200 OK):**
    ```json
    {
      "status": "apto",
      "advogado": {
        "nome": "Dra. Ana Costa",
        "oab": "MA12345",
        "start_time": "2025-09-21T23:30:00.123456"
      }
    }
    ```
-   **Resposta de Falha (Código 401 Unauthorized):**
    ```json
    {
      "status": "negado",
      "mensagem": "Credenciais inválidas."
    }
    ```

### **2. `GET /session_info`**

Recupera as informações da sessão ativa. Ideal para ser chamado a cada segundo pelo frontend para atualizar o painel de monitoramento.

-   **URL:** `/session_info`
-   **Método:** `GET`
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "nome": "Dra. Ana Costa",
      "oab": "MA12345",
      "tempo_de_uso": "0:15:42"
    }
    ```
-   **Resposta de Falha (404 Not Found):** (Se não houver sessão ativa)
    ```json
    {
      "error": "Nenhuma sessão ativa."
    }
    ```

### **3. `POST /logout`**

Encerra a sessão do advogado no backend, limpando os dados do usuário logado.

-   **URL:** `/logout`
-   **Método:** `POST`
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "status": "sucesso",
      "mensagem": "Sessão encerrada."
    }
    ```

### **4. `POST /shutdown`**

Instrui o servidor backend a se desligar. Ideal para ser chamado pelo Electron quando a aplicação principal for fechada, para garantir que nenhum processo Python fique rodando em segundo plano.

-   **URL:** `/shutdown`
-   **Método:** `POST`
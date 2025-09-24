# Backend - Sistema de Acesso OAB (v3.0)

Este é o serviço de backend em Python para a aplicação de quiosque da OAB. Ele gerencia a autenticação, sessões de uso com tempo limite, e cotas de impressão através de uma API local.

## Setup do Ambiente

1.  Certifique-se de ter o Python 3.10+ instalado.
2.  Abra um terminal na pasta do projeto e instale as dependências:
    ```
    pip install -r requirements.txt
    ```

## Como Iniciar o Servidor

Para iniciar o backend, execute o seguinte comando no terminal:

```
python backend.py
```

O servidor estará disponível no endereço `http://127.0.0.1:5000`.

## Documentação da API

### **1. `POST /login`**

Autentica o advogado e inicia uma nova sessão de uso.

-   **Corpo da Requisição (JSON):**
    ```json
    {
      "oab": "MA654321",
      "cpf": "222.22-22",
      "nascimento": "15/07/1992",
      "mac_address": "00:1A:2B:3C:4D:5E"
    }
    ```
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "status": "apto",
      "advogado": {
        "nome": "Dra. Maria Oliveira",
        "oab": "MA654321",
        "tipo": "advogado",
        "start_time": "...",
        "limite_minutos": 180,
        "notificacoes_enviadas": []
      }
    }
    ```
-   **Resposta de Falha (401 Unauthorized):**
    ```json
    {
      "status": "negado",
      "mensagem": "Credenciais inválidas ou usuário inativo."
    }
    ```

### **2. `GET /session_info`**

Recupera o status atual da sessão. Este é o endpoint principal para monitoramento.

-   **Como Usar:** O frontend (Electron) deve chamar este endpoint a cada X segundos (ex: 10 segundos) para manter as informações atualizadas.

-   **URL (com query parameter):** `/session_info?oab=MA654321`

-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "nome": "Dra. Maria Oliveira",
      "oab": "MA654321",
      "tipo": "advogado",
      "tempo_de_uso": "0:05:32",
      "tempo_restante_formatado": "2:54:28",
      "forcar_logout": false,
      "notificacao": "Atenção: Restam aproximadamente 150 minutos na sua sessão."
    }
    ```
-   **Guia para o Frontend (Electron):**
    * **`forcar_logout`**: Se este valor vier como `true`, o frontend deve imediatamente encerrar a sessão do usuário e voltar para a tela de login.
    * **`notificacao`**: Se este valor contiver um texto (não for `null`), o frontend deve exibi-lo em uma janela de pop-up para o usuário.

### **3. `POST /imprimir`**

Calcula o custo de uma solicitação de impressão e registra o evento se confirmado.

-   **Como Usar:** O frontend envia a quantidade de páginas que o usuário deseja imprimir. O backend responde com o cálculo de custos. O frontend deve exibir essa resposta para o usuário e pedir confirmação antes de efetivamente enviar para a impressora.

-   **Corpo da Requisição (JSON):**
    ```json
    {
      "oab": "MA654321",
      "paginas_solicitadas": 40
    }
    ```
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
        "status": "calculado",
        "mensagem_para_usuario": "Das 40 páginas, 20 são gratuitas. As 20 páginas restantes custarão R$ 10.00.",
        "paginas_cobradas": 20,
        "custo_total": "10.00"
    }
    ```
-   **Guia para o Frontend (Electron):**
    * O frontend deve exibir a `mensagem_para_usuario` em uma caixa de diálogo com botões "Confirmar" e "Cancelar".

### **4. `POST /logout`**

Encerra a sessão do advogado no backend.

-   **Corpo da Requisição (JSON):**
    ```json
    {
      "oab": "MA654321"
    }
    ```
-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "status": "sucesso",
      "mensagem": "Sessão encerrada."
    }
    ```

### **5. `GET /mac_address`**
Retorna o endereço MAC da máquina onde o servidor está rodando.

-   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "mac_address": "00:E0:4C:1D:5B:B4"
    }
    ```
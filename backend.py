from flask import Flask, request, jsonify
from datetime import datetime
import sys
import logging

# Inicia o sistema de logging para registrar eventos da aplicação no terminal.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Mock de banco de dados. Esta lista será substituída pela lógica de consulta à API real.
advogados_aptos = [
    {
        "oab": "MA123456",
        "nascimento": "01/01/1980",
        "cpf": "111.111.111-11",
        "nome": "Dr. João da Silva"
    },
    {
        "oab": "MA654321",
        "nascimento": "15/07/1992",
        "cpf": "222.222.222-22",
        "nome": "Dra. Maria Oliveira"
    },
    {
        "oab": "MA12345",
        "nascimento": "10/05/1985",
        "cpf": "333.333.333-33",
        "nome": "Dra. Ana Costa"
    }
]

# Armazena em memória a sessão do usuário atualmente logado.
current_session = {}

# --- Endpoints da API ---

@app.route('/login', methods=['POST'])
def login():
    """Valida as credenciais do usuário e inicia uma sessão."""
    global current_session
    dados = request.json
    logging.info(f"Recebida tentativa de login para OAB: {dados.get('oab')}")
    
    # TODO: Substituir a validação em loop pela chamada à API real.
    for advogado in advogados_aptos:
        if advogado["oab"] == dados.get('oab') and advogado["cpf"] == dados.get('cpf'):
            current_session = {
                "nome": advogado["nome"],
                "oab": advogado["oab"],
                "start_time": datetime.now().isoformat()
            }
            logging.info(f"Login bem-sucedido para {advogado['nome']}")
            return jsonify({
                "status": "apto",
                "advogado": current_session
            })
    
    logging.warning(f"Login falhou para OAB: {dados.get('oab')}")
    return jsonify({"status": "negado", "mensagem": "Credenciais inválidas."}), 401

@app.route('/session_info', methods=['GET'])
def get_session_info():
    """Retorna as informações da sessão ativa, incluindo o tempo de uso."""
    if not current_session:
        return jsonify({"error": "Nenhuma sessão ativa."}), 404
    
    start_time = datetime.fromisoformat(current_session["start_time"])
    elapsed_time = datetime.now() - start_time
    
    info = {
        "nome": current_session.get("nome"),
        "oab": current_session.get("oab"),
        "tempo_de_uso": str(elapsed_time).split('.')[0]
    }
    return jsonify(info)

@app.route('/logout', methods=['POST'])
def logout():
    """Encerra a sessão ativa do usuário."""
    global current_session
    if current_session:
        logging.info(f"Sessão encerrada para {current_session.get('nome')}")
        current_session = {}
    return jsonify({"status": "sucesso", "mensagem": "Sessão encerrada."})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Endpoint para permitir que o processo principal encerre o servidor Flask."""
    logging.info("Comando de desligamento recebido. Encerrando o servidor.")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        sys.exit()
    func()
    return "Servidor encerrando..."

# Bloco de execução principal: Inicia o servidor Flask.
if __name__ == '__main__':
    logging.info("Servidor de backend iniciando em http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
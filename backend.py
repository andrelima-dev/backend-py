from flask import Flask, request, jsonify
from datetime import datetime, date, timedelta
import sys
import logging
import uuid

# --- CONFIGURAÇÕES GLOBAIS DO SISTEMA ---
# Deixar as regras de negócio aqui facilita a manutenção futura.
CONFIG = {
    "limites_tempo_minutos": {
        "advogado": 180,
        "estagiario": 120
    },
    "cota_impressoes_gratis_dia": 20,
    "custo_por_pagina_excedente_reais": 0.50, # Valor dinâmico para impressão
    "notificacoes_advogado_minutos": [30, 90, 120, 150, 170],
    "notificacoes_estagiario_minutos": [30, 60, 90, 110]
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# --- Mock de Banco de Dados ---
advogados_aptos = [
    {"oab": "MA654321", "nascimento": "15/07/1992", "cpf": "222.222.222-22", "nome": "Dra. Maria Oliveira", "tipo": "advogado"},
    {"oab": "MA12345", "nascimento": "10/05/1985", "cpf": "333.333.333-33", "nome": "Dr. Carlos Mendes", "tipo": "estagiario"}
]
sessions = {} # Armazena as sessões ativas
impressoes = {} # Armazena o log de impressões

# --- Endpoints da API ---

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    if dados is None:
        return jsonify({"Erro": "Dados JSON não enviados ou inválidos."}), 400
    oab, cpf, nascimento, mac = dados.get('oab'), dados.get('cpf'), dados.get('nascimento'), dados.get('mac_address')
    logging.info(f"Recebida tentativa de login para OAB: {oab} da máquina {mac}")

    if not all([oab, cpf, nascimento, mac]):
        return jsonify({"Erro": "Dados incompletos são obrigatórios."}), 400

    for advogado in advogados_aptos:
        if advogado["oab"] == oab and advogado["cpf"] == cpf and advogado["nascimento"] == nascimento:
            user_type = advogado["tipo"]
            sessions[oab] = {
                "nome": advogado["nome"], "oab": advogado["oab"], "tipo": user_type,
                "start_time": datetime.now(),
                "limite_minutos": CONFIG["limites_tempo_minutos"].get(user_type, 120), # Pega o limite do config
                "notificacoes_enviadas": [] # Lista para controlar as notificações
            }
            logging.info(f"Login bem-sucedido para {advogado['nome']}")
            return jsonify({"status": "apto", "advogado": sessions[oab]})
    
    return jsonify({"status": "negado", "mensagem": "Credenciais inválidas ou usuário inativo."}), 401


@app.route('/session_info', methods=['GET'])
def get_session_info():
    oab = request.args.get('oab')
    if not oab or oab not in sessions:
        return jsonify({"error": f"Nenhuma sessão ativa para este OAB."}), 404
    
    session = sessions[oab]
    start_time = session["start_time"]
    limite_minutos = session["limite_minutos"]
    
    elapsed_time = datetime.now() - start_time
    elapsed_minutes = int(elapsed_time.total_seconds() / 60)
    
    tempo_restante_segundos = (limite_minutos * 60) - elapsed_time.total_seconds()
    
    # Logica do controle de tempo
    forcar_logout = tempo_restante_segundos <= 0
    notificacao = None
    
    # Define os pontos de notificação com base no tipo de usuário
    milestones = CONFIG.get(f"notificacoes_{session['tipo']}_minutos", [])
    
    # Verifica se o tempo atual passou de um marco de notificação
    for milestone in milestones:
        if elapsed_minutes >= milestone and milestone not in session["notificacoes_enviadas"]:
            minutos_restantes = limite_minutos - milestone
            notificacao = f"Atenção: Restam aproximadamente {minutos_restantes} minutos na sua sessão."
            if minutos_restantes <= 10:
                notificacao = f"ATENÇÃO: Sua sessão será encerrada em menos de {minutos_restantes} minutos!"
            session["notificacoes_enviadas"].append(milestone)
            break # Envia apenas uma notificação por vez
            
    info = {
        "nome": session.get("nome"),
        "oab": session.get("oab"),
        "tipo": session.get("tipo"),
        "tempo_de_uso": str(elapsed_time).split('.')[0],
        "tempo_restante_formatado": str(timedelta(seconds=int(max(0, tempo_restante_segundos)))).split('.')[0],
        "forcar_logout": forcar_logout,
        "notificacao": notificacao 
    }
    return jsonify(info)

@app.route('/imprimir', methods=['POST'])
def imprimir():
    dados = request.json
    if dados is None:
        return jsonify({"error": "Dados JSON não enviados ou inválidos."}), 400
    oab = dados.get('oab')
    paginas_solicitadas = dados.get('paginas_solicitadas', 0)

    if not oab or oab not in sessions:
        return jsonify({"error": "Sessão inválida."}), 401
    
    hoje = date.today().isoformat()
    impressoes.setdefault(oab, {}).setdefault(hoje, 0)
    
    impressoes_ja_feitas = impressoes[oab][hoje]
    cota_gratis = CONFIG["cota_impressoes_gratis_dia"]
    
    # Logica calculo impressão
    paginas_gratuitas_nesta_solicitacao = max(0, cota_gratis - impressoes_ja_feitas)
    paginas_cobradas = max(0, paginas_solicitadas - paginas_gratuitas_nesta_solicitacao)
    
    custo_total = paginas_cobradas * CONFIG["custo_por_pagina_excedente_reais"]
    
    # Atualiza a contagem de impressões do dia
    impressoes[oab][hoje] += paginas_solicitadas
    
    mensagem = f"Das {paginas_solicitadas} páginas, {min(paginas_solicitadas, paginas_gratuitas_nesta_solicitacao)} são gratuitas."
    if paginas_cobradas > 0:
        mensagem += f" As {paginas_cobradas} páginas restantes custarão R$ {custo_total:.2f}."
        
    logging.info(f"Cálculo de impressão para {sessions[oab]['nome']}: {mensagem}")
    
    return jsonify({
        "status": "calculado",
        "mensagem_para_usuario": mensagem,
        "paginas_cobradas": paginas_cobradas,
        "custo_total": f"{custo_total:.2f}"
    })

# ... (outros endpoints como logout, mac_address, etc., continuam iguais) ...

if __name__ == '__main__':
    logging.info("Servidor de backend iniciando em http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
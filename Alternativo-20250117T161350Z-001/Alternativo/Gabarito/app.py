# =====================================================================================
# ARQUIVO: app.py
# FUNÇÃO: Servidor backend da aplicação de chat. (Versão aprimorada)
# DESCRIÇÃO: Este script utiliza Flask para criar as rotas web e Flask-SocketIO
#            para gerenciar a comunicação em tempo real (mensagens de chat).
# =====================================================================================
from flask import Flask, render_template, request, redirect, url_for # estruturas para criar o site
from flask_socketio import SocketIO, send, emit # estruturas para criar o chat

import random # para escolher cores aleatórias


# Cria o site e informa que a pasta de templates é o diretório atual ('.')
# POR QUÊ? Por padrão, o Flask procura templates em uma pasta chamada 'templates'.
#          Como nossos arquivos HTML estão no mesmo diretório que app.py,
#          especificamos `template_folder='.'` para ajustar esse comportamento.
app = Flask(__name__, template_folder='.')
app.config["SECRET_KEY"] = "ajuiahfa78fh9f78shfs768fgs7f6" # chave de seguranca, pode ser qualquer coisa, mas escolha algo dificil

# Inicializa o SocketIO, permitindo que o servidor se comunique em tempo real.
# POR QUÊ `cors_allowed_origins`? Isso é uma medida de segurança. `"*"` permite que
# qualquer cliente (de qualquer endereço) se conecte ao nosso servidor, o que é
# ideal para desenvolvimento e testes em rede local.
socketio = SocketIO(app, cors_allowed_origins="*") # cria a conexão entre diferentes máquinas que estão no mesmo site

# Lista de cores de fundo seguras que têm bom contraste com texto branco.
# POR QUÊ? Escolhemos cores que não são muito claras para garantir que o texto
#          branco permaneça legível.
CORES_USUARIOS = [
    "#B91C1C", "#B45309", "#047857", "#1D4ED8", "#6D28D9", "#BE185D",
    "#15803D", "#991B1B", "#9A3412", "#065F46", "#1E40AF", "#5B21B6",
    "#9D174D", "#4338CA", "#008080", "#800080", "#C53030", "#2C5282"
]

# Cria uma cópia da lista de cores para gerenciar as cores disponíveis.
# POR QUÊ? Para garantir que cada usuário tenha uma cor única, removemos uma cor
#          desta lista quando um usuário entra e a devolvemos quando ele sai.
cores_disponiveis = CORES_USUARIOS[:]

# Dicionário para armazenar a relação entre o ID da sessão (sid) e o nome de usuário.
# POR QUÊ? Isso permite que o servidor saiba qual nome de usuário corresponde a qual
#          conexão, tornando possível incluir o nome do remetente nas mensagens.
usuarios_conectados = {}

# Dicionário para armazenar o histórico de mensagens.
# POR QUÊ? Para que possamos buscar o texto de uma mensagem original quando
#          alguém a responde. A chave será o ID da mensagem e o valor, os dados da mensagem.
historico_mensagens = {}

def get_sid():
    """
    Função auxiliar para obter o ID da sessão (sid) do request atual.
    O atributo `sid` é adicionado ao objeto `request` pelo Flask-SocketIO
    durante o contexto de um evento, mas não é reconhecido por
    analisadores de código estático, por isso o `# type: ignore`.
    """
    return request.sid # type: ignore

def get_user_info():
    """
    Função auxiliar para obter as informações do usuário conectado
    a partir do ID da sessão (sid) do request atual.
    """
    sid = get_sid()
    return usuarios_conectados.get(sid), sid

@socketio.on('connect')
def handle_connect():
    # Esta função é chamada automaticamente quando um novo cliente se conecta.
    print(f"Cliente conectado: {get_sid()}")

@socketio.on('join')
def handle_join(data):
    # Evento personalizado para o cliente "se apresentar" ao servidor.
    username = data.get('username', 'Anônimo')

    # Garante uma cor única para o usuário
    if cores_disponiveis:
        cor_usuario = random.choice(cores_disponiveis)
        cores_disponiveis.remove(cor_usuario)
    else:
        # Fallback: se as cores predefinidas acabarem, gera uma cor aleatória.
        cor_usuario = f"#{random.randint(0, 0xFFFFFF):06x}"

    sid = get_sid()
    usuarios_conectados[sid] = {"username": username, "color": cor_usuario}
    print(f"Usuário '{username}' (cor: {cor_usuario}) entrou no chat com o sid: {sid}")
    # Notifica os outros usuários que alguém entrou.
    # POR QUÊ `broadcast=True, include_self=False`? Para enviar a todos,
    # exceto para o próprio usuário que acabou de entrar.
    emit('user_update', {'message': f'{username} entrou no chat.'}, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    # Evento para quando um cliente se desconecta.
    # POR QUÊ? Para limpar o dicionário e liberar memória, removendo usuários
    #          que não estão mais ativos.
    sid = get_sid()
    user_info = usuarios_conectados.get(sid)
    if user_info:
        username = user_info['username']
        cor_devolvida = user_info.get('color')
        # Devolve a cor à lista de disponíveis se ela era da lista original
        if cor_devolvida in CORES_USUARIOS:
            cores_disponiveis.append(cor_devolvida)
        del usuarios_conectados[sid]
        print(f"Usuário '{username}' ({sid}) desconectado.")
        # Notifica a todos que o usuário saiu.
        emit('user_update', {'message': f'{username} saiu do chat.'}, broadcast=True)

@socketio.on('typing')
def handle_typing():
    user_info, sid = get_user_info()
    if user_info:
        emit('user_typing', {'username': user_info['username'], 'sid': sid}, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing():
    user_info, sid = get_user_info()
    if user_info:
        emit('user_stop_typing', {'username': user_info['username'], 'sid': sid}, broadcast=True, include_self=False)


@socketio.on("message") # define que a função abaixo vai ser acionada quando o evento de "message" acontecer
def gerenciar_mensagens(data):
    # O cliente agora envia um objeto em vez de apenas texto
    mensagem_texto = data.get('text')
    reply_to_id = data.get('reply_to')

    user_info, sid = get_user_info()
    if not user_info:
        return # Ignora a mensagem se o usuário não for encontrado
    
    # Cria um ID único para a mensagem atual
    message_id = f"{sid}_{random.randint(1000, 9999)}"

    payload = {"id": message_id, "text": mensagem_texto, "sid": sid, "username": user_info['username'], "color": user_info['color']}
    
    # Se for uma resposta, busca a mensagem original e a anexa ao payload
    if reply_to_id and reply_to_id in historico_mensagens:
        original_message = historico_mensagens[reply_to_id]
        payload['reply_context'] = {'username': original_message['username'], 'text': original_message['text']}

    # Armazena a mensagem atual no histórico para futuras respostas
    historico_mensagens[message_id] = payload

    print(f"Mensagem de '{user_info['username']}' ({sid}): {mensagem_texto}")
    # Usamos emit() em vez de send() para maior clareza.
    # send(payload) é um atalho para emit('message', payload).
    # Usar emit() é mais explícito e melhor compreendido por ferramentas de análise.
    emit("message", payload, broadcast=True)

@app.route("/") # cria a página do site
def login():
    # COMO FUNCIONA: Esta é a rota principal do site. Quando alguém acessa o
    #               endereço base (ex: http://localhost:5000), o Flask renderiza
    #               e envia a página `login.html` para o navegador do usuário.
    # A rota principal agora serve a página de login.
    return render_template("login.html")

@app.route("/chat")
def chat():
    # COMO FUNCIONA: Esta rota é acessada após o login. Ela pega o nome de usuário
    #               passado como parâmetro na URL (ex: /chat?username=Joao).
    # POR QUÊ? Ela injeta o nome de usuário no template `index.html`, personalizando
    #          a página de chat para cada usuário.
    username = request.args.get('username')

    # Validação: Se o nome de usuário não for fornecido ou estiver em branco,
    # redireciona o usuário de volta para a página de login.
    if not username or not username.strip():
        return redirect(url_for('login'))

    return render_template("index.html", username=username.strip())

if __name__ == "__main__":
    # Inicia a aplicação.
    # POR QUÊ `host='0.0.0.0'`? Isso faz com que o servidor seja acessível por
    # qualquer dispositivo na mesma rede, não apenas pelo próprio computador (localhost).
    # Essencial para o teste em rede local.
    socketio.run(app, host='0.0.0.0', port=5000)
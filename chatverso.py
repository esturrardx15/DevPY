# =====================================================================================
# Copyright 2024 Estevão Teodoro
# Contato: est.teodoro@gmail.com
# Todos os direitos reservados.
# FUNÇÃO: Lançador de login para uso em rede local.
# DESCRIÇÃO: Este script cria uma página de login simples usando a biblioteca Flet.
#            Ele captura o nome do usuário e o redireciona para o servidor de chat
#            principal (app.py), automatizando a criação da URL de acesso.
# =====================================================================================
import flet as ft
import socket
import urllib.parse

# --- Configurações ---
APP_HOST = '0.0.0.0'  # Permite acesso na rede local
APP_PORT = 8550       # Porta para esta aplicação de login

def get_local_ip():
    """Tenta descobrir o endereço IP local da máquina na rede."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Conecta-se a um IP externo (não envia dados) para descobrir qual interface de rede seria usada.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Se falhar, retorna um valor padrão para ser tratado.
        return None

# Tenta obter o IP local automaticamente. Se falhar, usa o IP de fallback.
# !! IMPORTANTE !! Se a detecção automática falhar ou se o servidor estiver em OUTRA máquina,
#                  defina o IP correto na variável CHAT_SERVER_IP_FALLBACK.
CHAT_SERVER_IP_FALLBACK = "10.14.222.137"
CHAT_SERVER_IP = get_local_ip() or CHAT_SERVER_IP_FALLBACK
CHAT_SERVER_PORT = 5000  # Porta do servidor de chat principal (app.py)
# ---------------------


def main(pagina):
    """Função principal que constrói e gerencia a interface do Flet."""

    pagina.title = "ChatVerso"
    # Centraliza todo o conteúdo da página
    pagina.vertical_alignment = ft.MainAxisAlignment.CENTER
    pagina.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Título da aplicação
    titulo = ft.Text("ChatVerso", size=30)
    
    # Define os componentes da interface: um pop-up de login e um botão para abri-lo.
    caixa_nome = ft.TextField(label="Digite seu User", autofocus=True)
    botao_popup = ft.ElevatedButton("Acessar Chat")
    
    popup = ft.AlertDialog(
        title=ft.Text("Seja bem-vindo ao ChatVerso"),
        content=caixa_nome,
        actions=[botao_popup]
    )
    
    botao = ft.ElevatedButton("Iniciar conversa")
    
    def entrar_chat(evento):
        # COMO FUNCIONA: Esta função é chamada quando o usuário clica em "Acessar Chat".
        if caixa_nome.value.strip():
            username = caixa_nome.value.strip()
            # POR QUÊ `urllib.parse.quote`? Garante que caracteres especiais no nome de
            # usuário (como espaços) sejam formatados corretamente para uso em uma URL.
            encoded_username = urllib.parse.quote(username)
            # Fecha o popup
            popup.open = False
            
            # Abre a URL do chat web no navegador padrão
            # POR QUÊ? Em vez de o usuário montar a URL manualmente, este script
            #          faz isso por ele, obtendo o IP do servidor de chat e
            #          adicionando o nome de usuário como parâmetro.
            pagina.launch_url(f"http://{CHAT_SERVER_IP}:{CHAT_SERVER_PORT}/chat?username={encoded_username}")
            
            # Limpa a tela do Flet e exibe uma mensagem de confirmação
            # para informar ao usuário que a ação foi bem-sucedida.
            pagina.clean()
            pagina.add(ft.Text(f"Chat aberto no seu navegador! Você pode fechar esta janela.", size=16))
            pagina.update()
    
    botao_popup.on_click = entrar_chat
    caixa_nome.on_submit = entrar_chat
    
    def abrir_popup(evento):
        # Simplesmente abre o diálogo de login quando o botão inicial é clicado.
        popup.open = True
        caixa_nome.focus() # Adiciona foco ao campo de texto ao abrir o popup
        pagina.update()
    
    botao.on_click = abrir_popup

    # adicionar elementos na pagina
    # Adiciona o diálogo à sobreposição da página. Isso é necessário para que ele possa ser aberto.
    # POR QUÊ? Em Flet, diálogos e outros elementos flutuantes devem ser
    #          adicionados à camada `overlay` antes de serem exibidos.
    pagina.overlay.append(popup)

    pagina.add(titulo, botao)


if __name__ == "__main__":
    # Imprime as URLs de acesso para o usuário.
    # POR QUÊ? Em vez de abrir o navegador automaticamente (o que pode causar o erro
    #          ERR_ADDRESS_INVALID com '0.0.0.0'), mostramos ao usuário os links
    #          corretos para que ele possa abrir manualmente.
    local_ip = get_local_ip() or "SEU_IP_DE_REDE"
    print("\n" + "="*50)
    print("🚀 Lançador do ChatVerso iniciado!")
    print(f"Acesse no seu navegador (na mesma máquina): http://localhost:{APP_PORT}")
    print(f"Acesse de outros dispositivos na mesma rede: http://{local_ip}:{APP_PORT}")
    print("="*50 + "\n")

    # Inicia a aplicação Flet como um servidor web, sem abrir o navegador automaticamente.
    ft.app(target=main, host=APP_HOST, port=APP_PORT)
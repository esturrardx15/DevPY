# Tela inicial:
    # Titul: LiveXet
    # Botao: Iniciar chat
        # quando clicar no botao:
        # abrir popup
            # Titulo: Boas vindas ao LiveXet
            # Caixa de texto: Digite seu user
            # Botao: entrar no Xet
                #fechar o popup
                # sumir titulo
                # sumir botao 'Iniciar xet'
                    # carregar chat
                    # carregar campo de enviar mensagem: "Digite sua mensagem"
                    # botao enviar
                        # enviar mensagem 
                        # limpar caixa de mensagem
                        
# pip install flet
# importar o flet
import flet as ft


#criar uma função principal para rodar o seu app
    # def nome_funcao(parametro):
        # o que a função vai fazer
        # passo 1
        # passo 2
        # passo 3
        # ...

def main(pagina):

    # titulo
    titulo = ft.Text("Live Xet")
    
    def enviar_mensagem_tunel(mensagem):
        #executar tudo que eu quero que aconteça para todos os usuarios que receberem a mensagem
        
        texto = ft.Text(mensagem)
        xet.controls.append(texto)
        pagina.update()
        
    pagina.pubsub.subscribe(enviar_mensagem_tunel)
    
    def enviar_mensagem(evento):
        nome_usuario = caixa_nome.value
        texto_campo_mensagem = campo_enviar_mensagem.value
        mensagem = f"{nome_usuario}: {texto_campo_mensagem}"
        pagina.pubsub.send_all(mensagem)
        # limpar caixa de enviar mensagem
        campo_enviar_mensagem.value=""
        pagina.update()

    campo_enviar_mensagem = ft.TextField(label="Digite sua mensagem", on_submit=enviar_mensagem)
    botao_enviar = ft.ElevatedButton("Enviar", on_click=enviar_mensagem)
    linha_enviar = ft.Row([campo_enviar_mensagem, botao_enviar])

    xet = ft.Column()
    

    def entrar_xet(evento):
        #fechar o popup
        popup.open = False
        # sumir titulo
        pagina.remove(titulo)
        # sumir botao 'Iniciar xet'
        pagina.remove(botao)
        # carregar chat
        pagina.add(xet)
        pagina.add(linha_enviar)        
        # adicionar mensagem "'Usuario' entrou no xet"
        nome_usuario = caixa_nome.value
        mensagem = f"{nome_usuario} entrou no Xet"
        pagina.pubsub.send_all(mensagem)
        pagina.update()  

    # criar o popup
    titulo_popup = ft.Text("Seja bem vindo ao Live Xet")
    caixa_nome = ft.TextField(label="Digite seu User", on_submit=entrar_xet)
    botao_popup = ft.ElevatedButton("Acessar Xet", on_click=entrar_xet)


    popup = ft.AlertDialog(title = titulo_popup, content = caixa_nome, actions =  [botao_popup])
    
    # botao inicial
    def abrir_popup(evento):
        # o que vai acontecer quando clicar no botao
        pagina.dialog = popup
        popup.open = True
        pagina.update()
  

    botao = ft.ElevatedButton("Iniciar conversa", on_click = abrir_popup)

    # adicionar elementos na pagina
    pagina.add(titulo)
    pagina.add(botao)



# executar essa função com o flet
ft.app(target=main, view=ft.WEB_BROWSER)
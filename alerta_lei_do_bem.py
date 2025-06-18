import os
import smtplib
from email.mime.text import MIMEText
from hashlib import sha256

import requests
from bs4 import BeautifulSoup

# --- Configurações Lidas do Ambiente (GitHub Secrets) ---
URL = "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/lei-do-bem/paginas/lotes"
# Busca as credenciais dos Secrets do GitHub
EMAIL_REMETENTE = os.getenv("GMAIL_ADDRESS")
SENHA_APP = os.getenv("GMAIL_APP_PASSWORD")
# Busca os emails e os transforma em uma lista
RECIPIENTS_STRING = os.getenv("RECIPIENT_EMAILS", "")
EMAIL_DESTINATARIO = RECIPIENTS_STRING.split(',') if RECIPIENTS_STRING else []
ARQUIVO_HASH = "hash_pagina.txt"
# --- Fim das Configurações ---

def enviar_email(assunto, corpo):
    if not all([EMAIL_REMETENTE, SENHA_APP, EMAIL_DESTINATARIO]):
        print("Erro: Credenciais de e-mail não configuradas nos Secrets. Abortando envio.")
        return

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = ", ".join(EMAIL_DESTINATARIO)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL_REMETENTE, SENHA_APP)
            smtp_server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        print(f"E-mail de notificação enviado para {len(EMAIL_DESTINATARIO)} destinatário(s) com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")


def verificar_site():
    print("Iniciando verificação do site da Lei do Bem...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        conteudo_alvo = soup.find(id='parent-fieldname-text')

        if not conteudo_alvo:
            print("Não foi possível encontrar o conteúdo alvo na página.")
            return

        hash_atual = sha256(conteudo_alvo.text.encode('utf-8')).hexdigest()

        # O GitHub Actions não salva arquivos entre execuções.
        # A lógica de comparar com um hash antigo não funciona da mesma forma.
        # A solução mais simples é enviar um e-mail sempre que a ação rodar com sucesso
        # ou implementar uma forma de guardar o hash antigo (ex: em outro secret, Gist, etc.)
        # Para simplificar o aprendizado, vamos focar em fazer o script rodar e enviar um email de teste.
        # A lógica de detecção de mudança pode ser um próximo passo.

        print("Verificação do site concluída com sucesso. O conteúdo foi lido.")
        enviar_email(
            "Teste do Alerta da Lei do Bem (GitHub Actions)",
            f"Este é um e-mail de teste para confirmar que o seu robô no GitHub Actions está funcionando.\n\n"
            f"O hash atual da página é: {hash_atual}"
        )

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")


if __name__ == "__main__":
    verificar_site()

import smtplib
import email.utils
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import ssl
import logging
import socket

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)

# Configuración del servidor de correo electrónico
EMAIL_HOST = '74.125.24.108'
EMAIL_PORT = 465
EMAIL_USER = os.getenv('TO_EMAIL') #el que recibe el correo
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM') #desde donde se envía el correo

context = ssl.create_default_context()

def send_email(to_email, subject, body):
    """
    Envía un correo de confirmación al usuario recién creado.

    Parámetros:
    - `to_email`: La dirección de correo electrónico del destinatario.
    - `username`: El nombre del usuario que se acaba de crear.

    """
    try:
    # Configurar el mensaje de correo
        msg = EmailMessage()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)
        # Establecer conexión con el servidor SMTP y enviar correo
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        _logger.info(f"Correo enviado satisfactoriamente")
    except socket.gaierror as dns_error: # Manejar error de DNS específicamente 
        _logger.error(f"Error de DNS al enviar el correo: {dns_error}")
    except smtplib.SMTPException as smtp_error:
        _logger.error(f"Error al enviar el correo {smtp_error}")
    except Exception as e:
        _logger.error(f"Error inesperado al enviar el correo {e}")
        
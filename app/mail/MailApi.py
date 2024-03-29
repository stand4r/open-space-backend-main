from ssl import create_default_context
from smtplib import SMTP_SSL
from config.config import (GMAIL_EMAIL, GMAIL_PASSWORD)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Union


class Mail():
    def __init__(self, mail: str, passwd: str) -> None:
        self._mail = mail
        self._passwd = passwd

    def _sendHtml(self, subject: str, to_addr: str, html: str) -> bool:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._mail
        message["To"] = to_addr
        part = MIMEText(html, "html")
        message.attach(part)
        try:
            self._session = SMTP_SSL('smtp.yandex.ru', context=create_default_context())
            self._session.login(self._mail, self._passwd)
            self._session.sendmail(self._mail, to_addr, message.as_string())
            self._session.close()
            return True
        except Exception as e:
            print(f"[Mail][sendHtml] error: {e}")
            return False
    
    def sendTemplate(self, code: Union[str, int], to_addr: str) -> bool:
        try:
            if isinstance(code, int):
                code = str(code)
            template = """\
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #f3f3f3;
                            color: #333333;
                            padding: 20px;
                        }
                        .container {
                            background-color: #ffffff;
                            padding: 20px;
                            margin: auto;
                            max-width: 600px;
                            border-radius: 8px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }
                        h2 {
                            color: #0066cc;
                        }
                        .code {
                            font-weight: bold;
                            font-size: 24px;
                            color: #0066cc;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Добро пожаловать в Open Space!</h2>
                        <p>Мы очень рады, что вы присоединились к нам.</p>
                        <p>Прежде чем вы сможете начать использовать все возможности учетной записи, вам необходимо подтвердить вашу электронную почту. Введите следующий код подтверждения на странице подтверждения электронной почты:</p>
                        <p class="code">"""+code+"""</p>
                    </div>
                </body>
                </html>
            """
            self._sendHtml(subject="Confirmation code", to_addr=to_addr, html=template)
            return True
        except:
            return False


mail = Mail(GMAIL_EMAIL, GMAIL_PASSWORD)
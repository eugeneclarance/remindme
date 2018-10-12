from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

line_bot_api = LineBotApi('NYP3d/KQtGCgtUePkY+GeeKibo/XJIVkykzC85sDzdkm2y10v/vQuOAqdm0L7LnVk9oIpd8llgk6g6PaGJxOFpcRnpdCpC2xXq42JBw/jnqk6ZtQ/BiOIzuahbuQWqUqJqzzs9wCZZ5srMW/iRzllQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ed4502914a6d64e62082db3af4f2fecd')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()

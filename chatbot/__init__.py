from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, SourceUser
)

from flask_sslify import SSLify
from . import db
import os

app = Flask(__name__)
sslify = SSLify(app)

app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
)

test_config = None
if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
else:
    app.config.from_mapping(test_config)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

line_bot_api = LineBotApi('NYP3d/KQtGCgtUePkY+GeeKibo/XJIVkykzC85sDzdkm2y10v/vQuOAqdm0L7LnVk9oIpd8llgk6g6PaGJxOFpcRnpdCpC2xXq42JBw/jnqk6ZtQ/BiOIzuahbuQWqUqJqzzs9wCZZ5srMW/iRzllQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ed4502914a6d64e62082db3af4f2fecd')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if isinstance(event.source, SourceUser):
        user_id = event.source.user_id

    x = 'SELECT message FROM messages WHERE userid = {} ORDER BY createdAt DESC LIMIT 2'.format(user_id)
    print(x)
    db_instance = db.get_db()
    last_message = db_instance.execute(
        x
    )

    if text == 'set':
        db_instance.execute(
            'INSERT INTO messages (userid, message)'
            ' VALUES (?, ?)',
            (user_id, text)
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please tell me your reminder title..'))

    if len(last_message) == 1:
        db_instance.execute(
            'INSERT INTO reminders (title, userid)'
            ' VALUES (?, ?)'
            (text, user_id)
        )
        db_instance.execute(
            'INSERT INTO messages (userid, message)'
            ' VALUES (?, ?)',
            (user_id, text)
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Please tell me your deadline..'))

    if len(last_message) == 2 and last_message[1] == 'set':
        db_instance.execute(
            'UPDATE reminders SET deadline'
            ' WHERE id = (SELECT id FROM reminders WHERE userid = {} ORDER BY createdAt LIMIT 1)'.format(user_id),
            (text)
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Thank you!'))

if __name__ == "__main__":
    app.run()
    db.init_app(app)

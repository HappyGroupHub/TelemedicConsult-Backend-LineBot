import yaml
from flask import Flask, request

import json
from yaml.loader import SafeLoader

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage

app = Flask(__name__)

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

line_bot_api = LineBotApi(config['Line']['channel_access_token'])
handler = WebhookHandler(config['Line']['channel_secret'])


@app.route("/", methods=['POST'])
def linebot():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        json_data = json.loads(body)
        handler.handle(body, signature)
        reply_token = json_data['events'][0]['replyToken']
        message_type = json_data['events'][0]['message']['type']
        if message_type == 'text':
            msg = json_data['events'][0]['message']['text']
            print("Received message: {}".format(msg))
            reply = msg
        else:
            reply = "Messages received are not in TEXT type."
        print("Replied with: {}".format(reply))
        line_bot_api.reply_message(reply_token, TextSendMessage(reply))
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
    return 'OK'


if __name__ == "__main__":
    app.run()
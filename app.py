import yaml
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    MessageAction, URIAction
from yaml.loader import SafeLoader

import database_connector

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

line_bot_api = LineBotApi(config['Line']['channel_access_token'])
handler = WebhookHandler(config['Line']['channel_secret'])

database = database_connector
app = Flask(__name__)


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "會員服務":
        carousel_template_message = TemplateSendMessage(
            alt_text="目錄 template",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://chickencutcut.files.wordpress.com/2015/05/img_6082.jpg",
                        title="初次使用請綁定Line",
                        text="若您已經在官網填寫完資料後，需要綁定Line即可使用完整服務",
                        actions=[
                            MessageAction(
                                label="點我綁定Line帳號",
                                text="綁定Line帳號"
                            ),

                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://cdn.discordapp.com/attachments/849850854743474187/1047449023772102686/169.png",
                        title='會員服務選擇',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='重新綁定LINE',
                                text='重新綁定LINE'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

    if event.message.text == "掛號":
        carousel_template_message = TemplateSendMessage(
            alt_text="目錄 template",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://chickencutcut.files.wordpress.com/2015/05/img_6082.jpg",
                        title="初次使用請綁定Line",
                        text="若您已經在官網填寫完資料後，需要綁定Line即可使用完整服務",
                        actions=[
                            MessageAction(
                                label="點我綁定Line帳號",
                                text="綁定Line帳號"
                            ),

                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://cdn.discordapp.com/attachments/849850854743474187/1047449023772102686/169.png",
                        title='會員服務選擇',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='重新綁定LINE',
                                text='重新綁定LINE'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)
    if event.message.text == "看診進度":
        carousel_template_message = TemplateSendMessage(
            alt_text="目錄 template",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://chickencutcut.files.wordpress.com/2015/05/img_6082.jpg",
                        title="初次使用請綁定Line",
                        text="若您已經在官網填寫完資料後，需要綁定Line即可使用完整服務",
                        actions=[
                            MessageAction(
                                label="點我綁定Line帳號",
                                text="綁定Line帳號"
                            ),

                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://cdn.discordapp.com/attachments/849850854743474187/1047449023772102686/169.png",
                        title='會員服務選擇',
                        text='請選擇',
                        actions=[
                            MessageAction(
                                label='重新綁定LINE',
                                text='重新綁定LINE'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

if __name__ == "__main__":
    app.run()
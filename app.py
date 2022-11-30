import yaml
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    MessageAction, TextSendMessage, FollowEvent
from yaml.loader import SafeLoader

import database_connector
import extra_functions

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

line_bot_api = LineBotApi(config['Line']['channel_access_token'])
handler = WebhookHandler(config['Line']['channel_secret'])

database = database_connector
extras = extra_functions

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


@handler.add(FollowEvent)
def handle_join(event):
    if event.type == "follow":
        database.update_line_registry(event.source.user_id, False)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_registry_ready = {}
    line_registry_id = {}
    line_registry_birthday = {}
    if line_registry_ready.get(event.source.user_id):
        if extras.is_id_legal(event.message.text):
            line_registry_id.pop(event.source.user_id, event.message.text)
            reply_message = "請依照範例輸入您的出生年月日 ex:1999/9/9"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        elif not extras.is_id_legal(event.message.text):
            reply_message = "您輸入的格式不符, 請再輸入一次!"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        elif event.source.user_id in line_registry_id:
            if extras.is_date(event.message.text):
                line_registry_birthday.pop(event.source.user_id, event.message.text)
                if line_registry_id.get(event.source.user_id) == database.get_patient_info(
                        line_registry_id.get(event.source.user_id).get('id')) & line_registry_birthday.get(
                    event.source.user_id) == database.get_patient_info(
                    line_registry_birthday.get(event.source.user_id).get('birthday')):
                    line_registry_ready.update(event.source.user_id, False)
                    database.update_patient_line_id(line_registry_id.get(event.source.user_id), event.source.user_id)
                    database.update_line_registry(event.source.user_id, True)
                    reply_message = "成功綁定"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                else:
                    line_registry_ready.update(event.source.user_id, False)
                    reply_message = "查無此人"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
            elif not extras.is_date(event.message.text):
                reply_message = "您輸入的格式不符, 請再輸入一次!"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

    if event.message.text == "綁定Line帳號":
        if not database.is_line_registered(event.source.user_id):
            line_registry_ready.pop(event.source.user_id, True)
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        else:
            reply_message = "您已經綁定Line帳號囉！ 若要重新綁定請點選會員服務"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

    if line_registry_ready.get(event.source.user_id):
        if extras.is_id_legal(event.message.text):
            line_registry_id.pop(event.source.user_id, event.message.text)
            reply_message = "請依照範例輸入您的出生年月日 ex:1999/9/9"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        elif extras.is_date(event.message.text):
            line_registry_birthday.pop(event.source.user_id, event.message.text)

            reply_message = "成功綁定"

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

from datetime import datetime

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

want_register = {}
temp_register_id = {}
temp_register_birthday = {}

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
        print("Someone just added you as friend")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_id = event.source.user_id
    message_received = event.message.text
    reply_token = event.reply_token

    # TODO(LD) Improve reply messages
    # TODO(LD) Check if patient has bind Line account via get_patient_info
    if want_register.get(line_id):
        if message_received == "離開":
            want_register[line_id] = False
            try:
                print("離開成功")
                reply_message = "已離開綁定程序"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                temp_register_id.pop(line_id)
            except KeyError:
                return 0
        elif line_id not in temp_register_id:  # 如果沒有輸入過身分證字號
            if extras.is_id_legal(message_received):  # 如果身份證字號符合規格
                temp_register_id[line_id] = message_received
                reply_message = "請依照範例輸入您的出生年月日 ex:1999/09/09"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif not extras.is_id_legal(message_received):  # 如果身份證字號不符合規格
                reply_message = "您輸入的格式不符, 請再輸入一次!"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif line_id in temp_register_id:  # 如果輸入過身分證字號
            if extras.is_date(message_received):  # 檢查生日是否符合規格
                temp_register_birthday[line_id] = datetime.strptime(message_received, '%Y/%m/%d')
                if database.get_patient_info(temp_register_id.get(line_id)) == "Error":  # 用ID確認是否有此病人
                    print(
                        "Line ID: {}\nDebug: Can't find patient's ID in patient_base table while binding Line account".format(
                            line_id))
                    want_register[line_id] = False
                    temp_register_id.pop(line_id)
                    temp_register_birthday.pop(line_id)
                    reply_message = "查無此人"
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                else:
                    if temp_register_birthday.get(
                            line_id).date() == database.get_patient_info(
                        temp_register_id.get(line_id)).get('birthday'):  # 驗證病人生日是否與資料庫相符
                        want_register[line_id] = False
                        database.update_patient_line_id(temp_register_id.get(line_id), line_id)
                        database.update_line_registry(line_id, True)
                        temp_register_id.pop(line_id)
                        temp_register_birthday.pop(line_id)
                        reply_message = "成功綁定"
                        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                    else:
                        want_register[line_id] = False
                        temp_register_id.pop(line_id)
                        temp_register_birthday.pop(line_id)
                        reply_message = "查無此人"
                        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif not extras.is_date(message_received):  # 如果輸入的生日不符合規格
                reply_message = "您輸入的格式不符, 請再輸入一次!"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "綁定Line帳號":
        if database.is_line_registered(line_id) == "Error":  # 確認病人在line_registry資料表中有資料
            database.create_line_registry(event.source.user_id, False)
            print("Line ID: {}\nDebug: Can't find user in line_registry table, create one by default".format(line_id))
            want_register[line_id] = True
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif not database.is_line_registered(line_id):  # 病人在line_registry有資料但為False
            want_register[line_id] = True
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        else:
            reply_message = "您已經綁定Line帳號囉！ 若要重新綁定請點選會員服務"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    # TODO(LD) Rename alt_text, it looks stupid now
    if message_received == "會員服務":
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
        line_bot_api.reply_message(reply_token, carousel_template_message)

    if message_received == "掛號":
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
        line_bot_api.reply_message(reply_token, carousel_template_message)
    if message_received == "看診進度":
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
        line_bot_api.reply_message(reply_token, carousel_template_message)


if __name__ == "__main__":
    app.run()

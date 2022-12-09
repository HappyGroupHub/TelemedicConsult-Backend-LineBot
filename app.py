from datetime import datetime

import yaml
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    MessageAction, TextSendMessage, FollowEvent, ConfirmTemplate
from yaml.loader import SafeLoader

import database as database
import utilities as utils

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

line_bot_api = LineBotApi(config['Line']['channel_access_token'])
handler = WebhookHandler(config['Line']['channel_secret'])

want_register = {}
want_re_register = {}
temp_register_id = {}
temp_register_birthday = {}


def processing_tasks(line_id):
    if want_register.get(line_id) or want_re_register.get(line_id):
        return True
    else:
        return False


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
    if want_register.get(line_id):
        if message_received == "離開":
            want_register.pop(line_id)
            try:
                reply_message = "已離開綁定程序"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                temp_register_id.pop(line_id)
            except KeyError:
                return 0
        elif line_id not in temp_register_id:  # 如果沒有輸入過身分證字號
            if utils.is_id_legal(message_received):  # 如果身份證字號符合規格
                temp_register_id[line_id] = message_received
                reply_message = "請輸入您的出生年月日\n範例:1999/09/09"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif not utils.is_id_legal(message_received):  # 如果身份證字號不符合規格
                reply_message = "身分證字號格式有誤，請再輸入一次\n注意：若要退出請輸入『離開』"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif line_id in temp_register_id:  # 如果輸入過身分證字號
            if want_re_register.get(line_id):  # 如果病人已在其他裝置上完成LINE綁定, 詢問是否複寫並重新綁定
                if message_received == "確定":
                    want_register.pop(line_id)
                    want_re_register.pop(line_id)
                    old_lind_id = database.get_patient_info_by_id(temp_register_id.get(line_id)).get('line_id')
                    database.update_patient_line_id(temp_register_id.get(line_id), line_id)
                    database.update_line_registry(old_lind_id, False)
                    database.update_line_registry(line_id, True)
                    temp_register_id.pop(line_id)
                    temp_register_birthday.pop(line_id)
                    reply_message = "成功轉移Line帳號，已斷開和舊裝置的連結"
                    push_message = "您已經轉移綁定至其他Line帳號，此裝置原有的連線已中斷，若你認為這是個錯誤請回報客服"
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                    line_bot_api.push_message(old_lind_id, TextSendMessage(text=push_message))
                elif message_received == "取消":
                    want_register.pop(line_id)
                    want_re_register.pop(line_id)
                    temp_register_id.pop(line_id)
                    temp_register_birthday.pop(line_id)
                    reply_message = "取消重新綁定流程"
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                else:
                    reply_message = "確認失敗，請重新輸入"
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif utils.is_date(message_received):  # 如果生日符合規格
                temp_register_birthday[line_id] = datetime.strptime(message_received, '%Y/%m/%d')
                if database.get_patient_info_by_id(temp_register_id.get(line_id)) == "Error":  # 如果無法用ID查到該病人
                    print(
                        "Line ID: {}\nDebug: Can't find patient's ID in patient_base table while binding Line account".format(
                            line_id))
                    want_register.pop(line_id)
                    temp_register_id.pop(line_id)
                    temp_register_birthday.pop(line_id)
                    reply_message = "查無此人"
                    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                else:  # 用病人ID確認有此病人
                    if temp_register_birthday.get(
                            line_id).date() == database.get_patient_info_by_id(
                        temp_register_id.get(line_id)).get('birthday'):  # 病人生日與資料庫相符
                        if database.get_patient_info_by_id(temp_register_id.get(line_id)).get(
                                'line_id') is None:  # 如果該病人沒綁定過LINE
                            want_register.pop(line_id)
                            database.update_patient_line_id(temp_register_id.get(line_id), line_id)
                            database.update_line_registry(line_id, True)
                            temp_register_id.pop(line_id)
                            temp_register_birthday.pop(line_id)
                            reply_message = "成功綁定"
                            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
                        elif database.get_patient_info_by_id(temp_register_id.get(line_id)).get(
                                'line_id') is not None:  # 如果病人已在其他裝置上完成LINE綁定, 詢問是否重新綁定
                            want_re_register[line_id] = True
                            template_message = TemplateSendMessage(
                                alt_text="已在其他裝置上完成LINE綁定，是否重新綁定?",
                                template=ConfirmTemplate(
                                    text="是否確定重新綁定並轉移帳號?\n------------注意------------\n確認後將斷開和舊裝置的連接",
                                    actions=[
                                        MessageAction(
                                            label="確定",
                                            text="確定"
                                        ),
                                        MessageAction(
                                            label="取消",
                                            text="取消"
                                        )
                                    ]
                                )
                            )
                            line_bot_api.reply_message(reply_token, template_message)
                    else:  # 病人生日與資料庫不相符
                        want_register.pop(line_id)
                        temp_register_id.pop(line_id)
                        temp_register_birthday.pop(line_id)
                        reply_message = "查無此人"
                        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif not utils.is_date(message_received):  # 如果生日不符合規格
                reply_message = "您輸入的格式不符, 請再輸入一次!"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if want_re_register.get(line_id) and not want_register.get(line_id):
        if message_received == "確定":
            want_re_register.pop(line_id)
            want_register[line_id] = True
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif message_received == "取消":
            want_re_register.pop(line_id)
            reply_message = "已取消"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        else:
            template_message = TemplateSendMessage(
                alt_text="無法辨識訊息，請重新選擇",
                template=ConfirmTemplate(
                    text="無法辨識訊息，請重新選擇\n若要要退出請則取消"
                         "",
                    actions=[
                        MessageAction(
                            label="確定",
                            text="確定"
                        ),
                        MessageAction(
                            label="取消",
                            text="取消"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(reply_token, template_message)

    if message_received == "綁定Line帳號" and not processing_tasks(line_id):
        if database.is_line_registered(line_id) == "Error":  # 如果病人在line_registry資料表中沒有資料
            database.create_line_registry(event.source.user_id, False)
            print("Line ID: {}\nDebug: Can't find user in line_registry table, create one by default".format(line_id))
            want_register[line_id] = True
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif not database.is_line_registered(line_id):  # 病人在line_registry有資料但為False
            want_register[line_id] = True
            reply_message = "請輸入您的身分證字號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        else:  # 病人在line_registry有資料但為True
            reply_message = "您已經綁定Line帳號囉！ 若要重新綁定請點選會員服務"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "重新綁定Line帳號" and not processing_tasks(line_id):
        if database.is_line_registered(line_id) == "Error":  # 如果病人在line_registry資料表中沒有資料
            database.create_line_registry(event.source.user_id, False)
            print("Line ID: {}\nDebug: Can't find user in line_registry table, create one by default".format(line_id))
            want_re_register[line_id] = True
            template_message = TemplateSendMessage(
                alt_text="尚未綁定Line帳號，是否進行初次綁定帳號",
                template=ConfirmTemplate(
                    text="您尚未綁定Line帳號，是否進行初次綁定帳號?",
                    actions=[
                        MessageAction(
                            label="確定",
                            text="確定"
                        ),
                        MessageAction(
                            label="取消",
                            text="取消"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(reply_token, template_message)
        elif not database.is_line_registered(line_id):  # 病人在line_registry有資料但為False
            want_re_register[line_id] = True
            template_message = TemplateSendMessage(
                alt_text="尚未綁定Line帳號，是否進行初次綁定帳號",
                template=ConfirmTemplate(
                    text="您尚未綁定Line帳號，是否進行初次綁定帳號?",
                    actions=[
                        MessageAction(
                            label="確定",
                            text="確定"
                        ),
                        MessageAction(
                            label="取消",
                            text="取消"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(reply_token, template_message)
        else:  # 病人在line_registry有資料但為True
            want_re_register[line_id] = True
            template_message = TemplateSendMessage(
                alt_text="綁定過帳號了，要不要重新綁定",
                template=ConfirmTemplate(
                    text="您已綁定過Line帳號\n請問是否要重新綁定?",
                    actions=[
                        MessageAction(
                            label="確定",
                            text="確定"
                        ),
                        MessageAction(
                            label="取消",
                            text="取消"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(reply_token, template_message)

    if message_received == "會員服務" and not processing_tasks(line_id):
        carousel_template_message = TemplateSendMessage(
            alt_text="會員服務",
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
                        title='重新綁定Line帳號',
                        text='若您已綁定過Line帳號\n請選擇重新綁定即可轉移帳號至新裝置',
                        actions=[
                            MessageAction(
                                label='點我重新綁定Line帳號',
                                text='重新綁定Line帳號'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(reply_token, carousel_template_message)

    if message_received == "掛號" and not processing_tasks(line_id):
        reply_message = "開發中..."
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "看診進度" and not processing_tasks(line_id):
        reply_message = "開發中..."
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "獲取個人資料(測試用)" and not processing_tasks(line_id):
        if database.is_line_registered(line_id):
            info = database.get_patient_info_by_line_id(line_id)
            reply_message = "姓名: {}\n身分證字號: {}\n生日: {}\n性別: {}".format(
                info.get('name'), info.get('id'), info.get('birthday'), info.get('sex'))
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif database.is_line_registered(line_id) == "Error":
            reply_message = "尚未綁定Line帳號，請先綁定Line帳號"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run()

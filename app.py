"""This is the main file of the program."""
import json
import time
from datetime import datetime

from flask import Flask, request, abort, Response
from flask.logging import create_logger
from flask_cors import CORS
from geventwebsocket import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, \
    CarouselColumn, \
    MessageAction, TextSendMessage, FollowEvent, ConfirmTemplate

import database
import utilities as utils

config = utils.read_config()
line_bot_api = LineBotApi(config.get('line_channel_access_token'))
handler = WebhookHandler(config.get('line_channel_secret'))

want_register = {}
want_re_register = {}
temp_register_id = {}
temp_register_birthday = {}
messages_to_send_to_frontend = []


def processing_tasks(line_id):
    """Check if there are any tasks' user is processing.

    :param str line_id: Line id of the user
    :rtype: bool
    """
    return bool(want_register.get(line_id) or want_re_register.get(line_id))


app = Flask(__name__)
CORS(app)
log = create_logger(app)


@app.route("/callback", methods=['POST'])
def callback():
    """Callback function for line webhook."""

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    log.info("Request body: %s", body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_join(event):
    """Handle when user add bot as friend."""

    if event.type == "follow":
        print("Someone just added you as friend")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle message event."""

    line_id = event.source.user_id
    message_received = event.message.text
    reply_token = event.reply_token

    # TODO(LD) Improve reply messages
    if want_register.get(line_id):
        if message_received == "離開":
            want_register.pop(line_id)
            reply_message = "已離開綁定程序"
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            try:
                temp_register_id.pop(line_id)
            except KeyError:
                pass
        elif line_id not in temp_register_id:  # 如果沒有輸入過身分證字號
            if utils.is_id_legal(message_received):  # 如果身份證字號符合規格
                temp_register_id[line_id] = message_received
                reply_message = "請輸入您的出生年月日\n範例:1999/09/09"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
            elif not utils.is_id_legal(message_received):  # 如果身份證字號不符合規格
                reply_message = "身分證字號格式有誤，再輸入一次\n注意：若要退出請輸入『離開』"
                line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))
        elif line_id in temp_register_id:  # 如果輸入過身分證字號
            if want_re_register.get(line_id):  # 如果病人已在其他裝置上完成LINE綁定, 詢問是否複寫並重新綁定
                if message_received == "確定":
                    want_register.pop(line_id)
                    want_re_register.pop(line_id)
                    old_lind_id = database.get_patient_info_by_id(
                        temp_register_id.get(line_id)).get('line_id')
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
                if database.get_patient_info_by_id(
                        temp_register_id.get(line_id)) == "Error":  # 如果無法用ID查到該病人
                    print(
                        f"Line ID: {line_id}\nDebug: Can't find patient's ID in patient_base table while binding Line account")
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
                            line_bot_api.reply_message(reply_token,
                                                       TextSendMessage(text=reply_message))
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
            database.create_line_registry(line_id, False)
            print(
                f"Line ID: {line_id}\nDebug: Can't find user in line_registry table, create one by default")
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
            database.create_line_registry(line_id, False)
            print(
                f"Line ID: {line_id}\nDebug: Can't find user in line_registry table, create one by default")
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
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1102477945643212820/1.png?width=1450&height=960",
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
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1102477945848746064/2.png?width=1450&height=960",
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

    if message_received == "看診功能" and not processing_tasks(line_id):
        carousel_template_message = TemplateSendMessage(
            alt_text="看診功能",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1102477946029084792/3.png?width=1450&height=960",
                        title="網站掛號",
                        text="您可以在此取得掛號連結，並進行掛號",
                        actions=[
                            MessageAction(
                                label="點我取得掛號連結",
                                text="傳送掛號連結"
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1105054810643898368/cc02260c1353954c.jpg?width=1087&height=720",
                        title='查詢預約',
                        text='您可以在此查詢您的預約',
                        actions=[
                            MessageAction(
                                label='點我查詢預約',
                                text='查詢預約'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1102477946247192627/4.png?width=1450&height=960",
                        title='查詢看診進度',
                        text='您可以在此查詢目前看診進度',
                        actions=[
                            MessageAction(
                                label='點我查詢看診進度',
                                text='查詢看診進度'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://media.discordapp.net/attachments/930101666861187172/1102477946448531516/5.png?width=1450&height=960",
                        title='過號報到',
                        text='若您過號了也不用擔心\n您可以點選過號報到，我們會盡快幫您安排看診',
                        actions=[
                            MessageAction(
                                label='點我過號報到',
                                text='過號報到'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(reply_token, carousel_template_message)

    if message_received == "傳送掛號連結" and not processing_tasks(line_id):
        reply_message = "http://localhost:5173//reservation.html"
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "查詢預約" and not processing_tasks(line_id):
        patient_id = database.get_patient_info_by_line_id(line_id)['id']
        undone_clinic_ids = database.get_patient_undone_clinic_ids(patient_id)
        if len(undone_clinic_ids) == 0:
            reply_message = "您沒有任何預約"
        else:
            reply_message = f"您這個月的預約有 {len(undone_clinic_ids)} 則 \n"
            for clinic_id in undone_clinic_ids:
                clinic_info = database.get_clinic_info(clinic_id)
                undone_appointment_info = database.get_patient_undone_appointment(clinic_id)
                reply_message += "\n----------------------------\n" \
                                 f"預約日期: {clinic_info['date']}\n" \
                                 f"預約時段: {clinic_info['time_period']}\n" \
                                 f"預約醫生: {clinic_info['doc_name']}\n" \
                                 f"預約號碼: {undone_appointment_info['appointment_num']}"
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "查詢看診進度" and not processing_tasks(line_id):
        patient_id = database.get_patient_info_by_line_id(line_id)['id']
        undone_clinic_ids = database.get_patient_undone_clinic_ids(patient_id)
        ongoing_appointment_info = database.get_patient_ongoing_appointment(patient_id)
        if len(undone_clinic_ids) == 0:
            reply_message = "您目前沒有預約"
        elif ongoing_appointment_info is None:
            clinic_info = database.get_clinic_info(undone_clinic_ids[0])
            undone_appointment_info = database.get_patient_undone_appointment(undone_clinic_ids[0])
            reply_message = "您目前沒有正在看診的預約\n" \
                            "這是您最近的預約\n" \
                            "------------------------\n" \
                            f"預約日期: {clinic_info['date']}\n" \
                            f"預約時段: {clinic_info['time_period']}\n" \
                            f"預約醫生: {clinic_info['doc_name']}\n" \
                            f"預約號碼: {undone_appointment_info['appointment_num']}"

        else:
            ongoing_clinic_info = database.get_patient_ongoing_clinic_info(
                ongoing_appointment_info['clinic_id'])
            reply_message = f"目前看診進度 : {ongoing_clinic_info['progress']} 號 \n" \
                            f"您的號碼 : {ongoing_appointment_info['appointment_num']} 號 \n" \
                            "---------------------------- \n" \
                            f"診間日期: {ongoing_clinic_info['date']}\n" \
                            f"診間時段: {ongoing_clinic_info['time_period']}\n" \
                            f"診間醫生: {ongoing_clinic_info['doc_name']}"
        line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_message))

    if message_received == "過號報到" and not processing_tasks(line_id):
        messages_to_send_to_frontend.append({'action': 'pass_appointment_check_in'})
        # patient_id = database.get_patient_info_by_line_id(line_id)['id']
        # ongoing_appointment_info = database.get_ongoing_appointment(patient_id)
        # if ongoing_appointment_info is not None:
        #     json_to_send = {'action': 'pass_appointment_check_in'}
        #     json_to_send.update(ongoing_appointment_info)
        #     to_frontend(json_to_send)


@app.route('/from_backend', methods=['POST'])
def from_backend():
    post_data = request.get_json()
    patient_name = post_data.get('patient_name')
    line_id = post_data.get('line_id')
    if post_data.get('action') == 'make_appointment':
        action_info = post_data.get('action_info')
        push_message = f"您好，{patient_name}\n" \
                       f"您已成功預約\n" \
                       f"以下為您的預約資訊\n" \
                       f"------------------------\n" \
                       f"預約日期: {action_info['date']}\n" \
                       f"預約時段: {action_info['time_period']}\n" \
                       f"預約醫生: {action_info['doc_name']}\n" \
                       f"預約號碼: {action_info['appointment_num']}\n" \
                       f"------------------------\n" \
                       f"請務必準時前往就醫，謝謝!"
        line_bot_api.push_message(line_id, TextSendMessage(text=push_message))
        return 'OK', 200
    if post_data.get('action') == 'notify_appointment':
        action_info = post_data.get('action_info')
        push_message = f"您好，{patient_name}\n" \
                       f"您預約於{action_info['date']}的線上門診已接近看診時間\n" \
                       f"屆時將傳送看診連結，請務必準時前往就醫，謝謝!" \
                       f"\n" \
                       f"您的預約號碼為：{action_info['appointment_num']}號\n" \
                       f"目前看診的進度為: {action_info['next_appointment_num']} 號\n" \
                       f"------------------------\n" \
                       f"預約日期: {action_info['date']}\n" \
                       f"預約時段: {action_info['time_period']}\n" \
                       f"預約醫生: {action_info['doc_name']}\n"
        line_bot_api.push_message(line_id, TextSendMessage(text=push_message))
        return 'OK', 200
    if post_data.get('action') == 'give_clinic_link':
        action_info = post_data.get('action_info')
        push_message = f"您好，{patient_name}\n" \
                       f"您預約於{action_info['date']}的線上門診已經輪到你看診囉!\n" \
                       f"請盡速點擊以下的連結進入診間!" \
                       f"\n" \
                       f"{action_info['link']}" \
                       f"------------------------\n" \
                       f"預約日期: {action_info['date']}\n" \
                       f"預約時段: {action_info['time_period']}\n" \
                       f"預約醫生: {action_info['doc_name']}\n"
        line_bot_api.push_message(line_id, TextSendMessage(text=push_message))
        return 'OK', 200
    if post_data.get('action') == 'pass_appointment':
        action_info = post_data.get('action_info')
        push_message = f"您好，{patient_name}\n" \
                       f"您預約由於{action_info['date']}的線上門診已經過號!\n" \
                       f"!!!！請勿點擊上方的連結!!!！\n" \
                       f"請點選「看診功能」-->「過號報到」\n" \
                       f"或直接輸入「過號報到」\n" \
                       f"屆時會再傳送提醒訊息!\n" \
                       f"請務必留意並準時進入診間，謝謝!"
        line_bot_api.push_message(line_id, TextSendMessage(text=push_message))
    else:
        abort(400)


def event_stream():
    while True:
        if messages_to_send_to_frontend:
            message = messages_to_send_to_frontend.pop(0)
            yield f"data: {json.dumps(message)}\n\n"
        time.sleep(1)  # to prevent CPU-intensive loop


@app.route('/stream')
def stream():
    print(f'Giving {messages_to_send_to_frontend}')
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(port=config.get('line_port'), debug=True, threaded=True)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Flask app running...")

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

import database
import utilities as utils

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

linebot_port = utils.read_config()['line_port']


@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    response = {'status': 'success'}
    post_data = request.get_json()
    name = post_data['name']
    id = post_data['id']
    sex = post_data['sex']
    birthday = post_data['birthday']
    blood_type = post_data['blood_type']
    ic_card_number = post_data['ic_card_number']
    phone_number = post_data['phone_number']
    address = post_data['address']
    height = post_data['height']
    weight = post_data['weight']
    ice_contact = post_data['ice_contact']
    ice_relation = post_data['ice_relation']
    ice_phone = post_data['ice_phone']
    database.register_patient(name, id, sex, birthday, blood_type, ic_card_number, phone_number,
                              address, height, weight, ice_contact, ice_relation, ice_phone)
    response['message'] = 'Patient registered successfully'
    return jsonify(response)


@app.route('/get_patient_info_by_id', methods=['GET', 'POST'])
def get_patient_info_by_id():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['id']
    patient_info = database.get_patient_info_by_id(patient_id)
    if 'birthday' in patient_info:
        patient_info['birthday'] = patient_info['birthday'].strftime("%Y-%m-%d")
    response.update(patient_info)
    return jsonify(response)


@app.route('/if_patient_registered_line', methods=['GET', 'POST'])
def if_patient_registered_line():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['id']
    patient_info = database.get_patient_info_by_id(patient_id)
    if patient_info['line_id'] is None or patient_info['line_id'] == '':
        response['registered'] = False
    else:
        response['registered'] = True
    return jsonify(response)


@app.route('/update_patient_info_by_id', methods=['GET', 'POST'])
def update_patient_info_by_id():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['id']
    phone_number = post_data['phone_number']
    address = post_data['address']
    height = post_data['height']
    weight = post_data['weight']
    ice_contact = post_data['ice_contact']
    ice_relation = post_data['ice_relation']
    ice_phone = post_data['ice_phone']
    database.update_patient_info_by_id(patient_id, phone_number, address, height, weight,
                                       ice_contact,
                                       ice_relation, ice_phone)
    return jsonify(response)


@app.route('/check_if_time_have_clinic', methods=['GET', 'POST'])
def check_if_time_have_clinic():
    response = {'status': 'success'}
    post_data = request.get_json()
    date = post_data['date']
    time_period = post_data['time_period']
    result = database.check_if_time_have_clinic(date, time_period)
    response.update(result)
    return jsonify(response)


@app.route('/get_clinic_info', methods=['GET', 'POST'])
def get_clinic_info():
    response = {'status': 'success'}
    post_data = request.get_json()
    clinic_id = post_data['clinic_id']
    clinic_info = database.get_clinic_info(clinic_id)
    if 'date' in clinic_info:
        clinic_info['date'] = clinic_info['date'].strftime("%Y-%m-%d")
    response.update(clinic_info)
    return jsonify(response)


@app.route('/update_clinic_status', methods=['GET', 'POST'])
def update_clinic_status():
    response = {'status': 'success'}
    post_data = request.get_json()
    clinic_id = post_data['clinic_id']
    status_dict = post_data['status_dict']
    database.update_clinic_status(clinic_id, **{
        'start_time': status_dict.get('start_time', None),
        'end_time': status_dict.get('end_time', None),
        'link': status_dict.get('link', None),
        'total_appointment': status_dict.get('total_appointment', None),
        'biggest_appointment_num': status_dict.get('biggest_appointment_num', None),
        'progress': status_dict.get('progress', None)
    })
    return jsonify(response)


@app.route('/make_appointment', methods=['GET', 'POST'])
def make_appointment():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    if database.check_can_patient_make_appointment(patient_id, clinic_id):
        appointment_num = database.make_appointment(clinic_id, patient_id)
        clinic_info = database.get_clinic_info(clinic_id)
        action_info = {'doc_name': clinic_info['doc_name'],
                       'date': clinic_info['date'].strftime("%Y-%m-%d"),
                       'time_period': clinic_info['time_period'],
                       'appointment_num': appointment_num}
        to_line(patient_id, 'make_appointment', **action_info)
        response['appointment_num'] = appointment_num
    else:
        response['appointment_num'] = 0
    return jsonify(response)


@app.route('/cancel_appointment', methods=['GET', 'POST'])
def cancel_appointment():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    database.cancel_appointment(patient_id, clinic_id)
    return jsonify(response)


@app.route('/get_patient_appointment_with_clinic_id', methods=['GET', 'POST'])
def get_patient_appointment_with_clinic_id():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    appointment_info = database.get_patient_appointment_with_clinic_id(patient_id, clinic_id)
    response.update(appointment_info)
    return jsonify(response)


@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    response = {'status': 'success'}
    post_data = request.get_json()
    doc_id = post_data['doc_id']
    password = post_data['password']
    doc_info = database.doctor_login(doc_id, password)
    response.update(doc_info)
    return jsonify(response)


@app.route('/get_doctor_clinic_list', methods=['GET', 'POST'])
def get_doctor_clinic_list():
    response = {'status': 'success'}
    post_data = request.get_json()
    doc_id = post_data['doc_id']
    clinic_list = database.get_doctor_clinic_list(doc_id)
    response['clinic_list'] = clinic_list
    return jsonify(response)


@app.route('/get_patients_by_clinic_id', methods=['GET', 'POST'])
def get_patients_by_clinic_id():
    response = {'status': 'success'}
    post_data = request.get_json()
    clinic_id = post_data['clinic_id']
    patients = database.get_patients_by_clinic_id(clinic_id)
    response['patients'] = patients
    return jsonify(response)


def to_line(patient_id, action, **action_info):
    patient_info = database.get_patient_info_by_id(patient_id)
    patient_name = patient_info['name']
    line_id = patient_info['line_id']
    post_data = {'patient_id': patient_id, 'patient_name': patient_name, 'line_id': line_id,
                 'action': action, 'action_info': action_info}
    requests.post(f'http://127.0.0.1:{linebot_port}/from_backend', json=post_data)


if __name__ == '__main__':
    app.run()

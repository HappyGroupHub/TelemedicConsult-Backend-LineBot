from flask import Flask, request, jsonify
from flask_cors import CORS

import database

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


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
    patient_info['birthday'] = patient_info['birthday'].strftime("%Y-%m-%d")
    response.update(patient_info)
    return jsonify(response)


@app.route('/if_patient_registered_line', methods=['GET', 'POST'])
def if_patient_registered_line():
    response = {'status': 'success'}
    post_data = request.get_json()
    patient_id = post_data['id']
    patient_info = database.get_patient_info_by_id(patient_id)
    if patient_info['line_id'] is None:
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


if __name__ == '__main__':
    app.run()

import time

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import database
import utilities as utils

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

config = utils.read_config()


@app.post('/register_patient')
async def register_patient(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    name = post_data['name']
    id = post_data['id']
    sex = post_data['sex']
    birthday = post_data['birthday']
    blood_type = post_data['blood_type']
    phone_number = post_data['phone_number']
    address = post_data['address']
    height = post_data['height']
    weight = post_data['weight']
    ice_contact = post_data['ice_contact']
    ice_relation = post_data['ice_relation']
    ice_phone = post_data['ice_phone']
    database.register_patient(name, id, sex, birthday, blood_type, phone_number,
                              address, height, weight, ice_contact, ice_relation, ice_phone)
    response['message'] = 'Patient registered successfully'
    return response


@app.post('/get_patient_info_by_id')
async def get_patient_info_by_id(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['id']
    patient_info = database.get_patient_info_by_id(patient_id)
    if 'birthday' in patient_info:
        patient_info['birthday'] = patient_info['birthday'].strftime("%Y-%m-%d")
    response.update(patient_info)
    return response


@app.post('/if_patient_registered_line')
async def if_patient_registered_line(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['id']
    patient_info = database.get_patient_info_by_id(patient_id)
    if patient_info['line_id'] is None or patient_info['line_id'] == '':
        response['registered'] = False
    else:
        response['registered'] = True
    return response


@app.post('/update_patient_info_by_id')
async def update_patient_info_by_id(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
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
    return response


@app.post('/check_if_time_have_clinic')
async def check_if_time_have_clinic(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    date = post_data['date']
    time_period = post_data['time_period']
    result = database.check_if_time_have_clinic(date, time_period)
    response.update(result)
    return response


@app.post('/get_clinic_info')
async def get_clinic_info(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    clinic_id = post_data['clinic_id']
    clinic_info = database.get_clinic_info(clinic_id)
    if 'date' in clinic_info:
        clinic_info['date'] = clinic_info['date'].strftime("%Y-%m-%d")
    response.update(clinic_info)
    return response


@app.post('/update_clinic_status')
async def update_clinic_status(request: Request):
    time.sleep(1.5)
    post_data = await request.json()
    response = {'status': 'success'}
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
    return response


@app.post('/make_appointment')
async def make_appointment(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    if database.check_can_patient_make_appointment(patient_id, clinic_id):
        appointment_num = database.make_appointment(clinic_id, patient_id)
        clinic_info = database.get_clinic_info(clinic_id)
        action_info = {'doc_name': clinic_info['doc_name'],
                       'date': clinic_info['date'].strftime("%Y-%m-%d"),
                       'time_period': clinic_info['time_period'],
                       'appointment_num': appointment_num}
        await to_line(patient_id, 'make_appointment', **action_info)
        response['appointment_num'] = appointment_num
    else:
        response['appointment_num'] = 0
    return response


@app.post('/cancel_appointment')
async def cancel_appointment(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    database.cancel_appointment(patient_id, clinic_id)
    clinic_info = database.get_clinic_info(clinic_id)
    action_info = {'doc_name': clinic_info['doc_name'],
                   'date': clinic_info['date'].strftime("%Y-%m-%d"),
                   'time_period': clinic_info['time_period'], }
    await to_line(patient_id, 'cancel_appointment', **action_info)
    return response


@app.post('/get_patient_appointment_with_clinic_id')
async def get_patient_appointment_with_clinic_id(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['patient_id']
    clinic_id = post_data['clinic_id']
    appointment_info = database.get_patient_appointment_with_clinic_id(patient_id, clinic_id)
    response.update(appointment_info)
    return response


@app.post('/doctor_login')
async def doctor_login(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    doc_id = post_data['doc_id']
    password = post_data['password']
    doc_info = database.doctor_login(doc_id, password)
    response.update(doc_info)
    return response


@app.post('/get_doctor_clinic_list')
async def get_doctor_clinic_list(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    doc_id = post_data['doc_id']
    clinic_list = database.get_doctor_clinic_list(doc_id)
    response['clinic_list'] = clinic_list
    return response


@app.post('/get_patient_reservation_list')
async def get_patient_reservation_list(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    patient_id = post_data['patient_id']
    reservation_list = database.get_unstarted_patient_reservation_appointments(patient_id)
    for appointment in reservation_list:
        clinic_info = database.get_clinic_info(appointment['clinic_id'])
        clinic_info['date'] = clinic_info['date'].strftime("%Y-%m-%d")
        appointment['clinic_info'] = clinic_info
    response['reservation_list'] = reservation_list
    return response


@app.post('/get_patients_by_clinic_id')
async def get_patients_by_clinic_id(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    clinic_id = post_data['clinic_id']
    patients = database.get_patients_by_clinic_id(clinic_id)
    patients_id = [patient['patient_id'] for patient in patients]
    patients_name = [patient['patient_name'] for patient in patients]
    appointment_nums = [patient['appointment_num'] for patient in patients]
    response['patients_id'] = patients_id
    response['patients_name'] = patients_name
    response['appointment_nums'] = appointment_nums
    response['patients'] = patients
    return response


@app.post('/next_appointment')
async def next_appointment(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    clinic_id = post_data['clinic_id']
    clinic_info = database.get_clinic_info(clinic_id)
    current_appointment_num = post_data['current_appointment_num']
    next_appointment_num = post_data['next_appointment_num']
    notify_appointment_num = post_data['notify_appointment_num']
    time.sleep(0.5)
    if current_appointment_num is not None or current_appointment_num != 0:
        database.update_appointment_end_time_to_now(clinic_id, current_appointment_num)
    if next_appointment_num is not None:
        patient_appointment = database.get_patient_appointment_with_clinic_id_and_appointment_num(
            clinic_id,
            next_appointment_num)
        patient_id = patient_appointment['patient_id']
        action_info = {'doc_name': clinic_info['doc_name'],
                       'date': clinic_info['date'].strftime("%Y-%m-%d"),
                       'time_period': clinic_info['time_period'],
                       'link': clinic_info['link']}
        await to_line(patient_id, 'give_clinic_link', **action_info)
        database.update_clinic_status(clinic_id,
                                      **{'start_time': None, 'end_time': None, 'link': None,
                                         'progress': next_appointment_num,
                                         'biggest_appointment_num': None,
                                         'total_appointment': None})
        database.update_appointment_start_time_to_now(clinic_id, next_appointment_num)
    if notify_appointment_num is not None:
        patient_appointment = database.get_patient_appointment_with_clinic_id_and_appointment_num(
            clinic_id,
            notify_appointment_num)
        patient_id = patient_appointment['patient_id']
        appointment_num = patient_appointment['appointment_num']
        action_info = {'doc_name': clinic_info['doc_name'],
                       'date': clinic_info['date'].strftime("%Y-%m-%d"),
                       'time_period': clinic_info['time_period'],
                       'appointment_num': appointment_num,
                       'next_appointment_num': next_appointment_num}
        await to_line(patient_id, 'notify_appointment', **action_info)
    return response


@app.post('/pass_appointment')
async def pass_appointment(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    clinic_id = post_data['clinic_id']
    clinic_info = database.get_clinic_info(clinic_id)
    appointment_num = post_data['appointment_num']
    patient_appointment = database.get_patient_appointment_with_clinic_id_and_appointment_num(
        clinic_id, appointment_num)
    patient_id = patient_appointment['patient_id']
    action_info = {'doc_name': clinic_info['doc_name'],
                   'date': clinic_info['date'].strftime("%Y-%m-%d"),
                   'time_period': clinic_info['time_period'],
                   'appointment_num': appointment_num}
    await to_line(patient_id, 'pass_appointment', **action_info)
    return response


@app.post('/clear_pass_appointment_time')
async def clear_pass_appointment_time(request: Request):
    post_data = await request.json()
    response = {'status': 'success'}
    clinic_id = post_data['clinic_id']
    appointment_num = post_data['appointment_num']
    time.sleep(1)
    database.clear_appointment_start_time_end_time(clinic_id, appointment_num)
    return response


async def to_line(patient_id, action, **action_info):
    patient_info = database.get_patient_info_by_id(patient_id)
    patient_name = patient_info['name']
    line_id = patient_info['line_id']
    post_data = {'patient_id': patient_id, 'patient_name': patient_name, 'line_id': line_id,
                 'action': action, 'action_info': action_info}
    requests.post(f'http://127.0.0.1:{config["line_port"]}/from_backend', json=post_data)


if __name__ == '__main__':
    uvicorn.run(app, port=5000)

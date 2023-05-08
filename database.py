"""This python file will handle all the database things."""
from datetime import datetime, timedelta

import mysql.connector as database

import utilities as utils

config = utils.read_config()

connection = database.connect(
    user=config.get('db_username'),
    password=config.get('db_password'),
    host=config.get('db_hostname'),
    database=config.get('db_name')
)

cursor = connection.cursor()


def register_patient(name, id, sex, birthday, blood_type, ic_card_number, phone_number, address,
                     height, weight,
                     ice_contact, ice_relation, ice_phone):
    try:
        statement = f"INSERT INTO patient_base (name, id, sex, birthday, blood_type, ic_card_number, phone_number, address, height, weight, ice_contact, ice_relation, ice_phone) VALUE ('{name}', '{id}', '{sex}', '{birthday}', '{blood_type}', '{ic_card_number}', '{phone_number}', '{address}', '{height}', '{weight}', '{ice_contact}', '{ice_relation}', '{ice_phone}')"
        cursor.execute(statement)
        connection.commit()
    except database.errors as error:
        print(f"Error creating patients to database: {error}")


def get_patient_info_by_id(patient_id):
    """Get patient info by patient id.

    :param str patient_id: Registered patient id
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM patient_base WHERE id = '{patient_id}'"
        cursor.execute(statement)
        for result in cursor:
            results = result
        patient_info = {
            'name': list(results)[0],
            'id': list(results)[1],
            'sex': list(results)[2],
            'birthday': list(results)[3],
            'blood_type': list(results)[4],
            'ic_card_number': list(results)[5],
            'phone_number': list(results)[6],
            'address': list(results)[7],
            'height': list(results)[8],
            'weight': list(results)[9],
            'ice_contact': list(results)[10],
            'ice_relation': list(results)[11],
            'ice_phone': list(results)[12],
            'line_id': list(results)[13]
        }
        return patient_info
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return "Error"
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return None


def get_patient_info_by_line_id(line_id):
    """Get patient info by line id.

    :param str line_id: Registered line id
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM patient_base WHERE line_id = '{line_id}'"
        cursor.execute(statement)
        for result in cursor:
            results = result
        patient_info = {
            'name': list(results)[0],
            'id': list(results)[1],
            'sex': list(results)[2],
            'birthday': list(results)[3],
            'blood_type': list(results)[4],
            'ic_card_number': list(results)[5],
            'phone_number': list(results)[6],
            'address': list(results)[7],
            'height': list(results)[8],
            'weight': list(results)[9],
            'ice_contact': list(results)[10],
            'ice_relation': list(results)[11],
            'ice_phone': list(results)[12],
            'line_id': list(results)[13]
        }
        return patient_info
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return "Error"
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return None


def update_patient_line_id(patient_id, line_id):
    """Update patient line id.

    :param str patient_id: Registered patient id
    :param str line_id: Registered line id
    """
    try:
        statement = f"UPDATE patient_base SET line_id = '{line_id}' WHERE id = '{patient_id}'"
        cursor.execute(statement)
        connection.commit()
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def update_patient_info_by_id(patient_id, phone_number, address, height, weight, ice_contact,
                              ice_relation, ice_phone):
    """Update patient info.

    :param phone_number: Patient phone number
    :param address: Patient address
    :param height: Patient height
    :param weight: Patient weight
    :param ice_contact: Patient ICE contact
    :param ice_relation: Patient ICE relation
    :param ice_phone: Patient ICE phone number
    :param str patient_id: Registered patient id
    """
    try:
        statement = f"UPDATE patient_base SET phone_number = '{phone_number}', address = '{address}', height = '{height}', weight = '{weight}', ice_contact = '{ice_contact}', ice_relation = '{ice_relation}', ice_phone = '{ice_phone}' WHERE id = '{patient_id}'"
        cursor.execute(statement)
        connection.commit()
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def is_line_registered(line_id):
    """Check if line id is registered.

    :param str line_id: Given line id
    :rtype: bool
    """
    try:
        connection.autocommit = True
        statement = f"SELECT is_registered FROM line_registry WHERE line_id = '{line_id}'"
        cursor.execute(statement)
        for result in cursor:
            is_registered = result
        return list(is_registered)[0]
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return 'Error'
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return 'Error'


def create_line_registry(line_id, is_registered=False):
    """Create line registry by given line id.

    This function will create a new line registry data by given line id.
    Only use this function when the given line id is not registered in line_registry table.
    And the is_registered parameter should be false by default.

    :param str line_id: Given line id
    :param bool is_registered: to registered or not (should be false by default)
    """
    try:
        statement = f"INSERT INTO line_registry (line_id, is_registered) VALUE ('{line_id}', {is_registered})"
        cursor.execute(statement)
        connection.commit()
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def update_line_registry(line_id, is_registered):
    """Update line registry.

    :param str line_id: Registered line id
    :param bool is_registered: to registered or not
    """
    try:
        statement = f"UPDATE line_registry SET is_registered = {is_registered} WHERE line_id = '{line_id}'"
        cursor.execute(statement)
        connection.commit()
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def check_if_time_have_clinic(date, time_period):
    """Check if the given time period have clinic.

    :param date: Given date
    :param time_period: Given time period
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT clinic_id FROM clinic_base WHERE date = '{date}' AND time_period = '{time_period}'"
        cursor.execute(statement)
        for result in cursor:
            clinic_id = result
            return {'have_clinic': True, 'clinic_id': list(clinic_id)[0]}
        return {'have_clinic': False, 'clinic_id': None}
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return {'have_clinic': False, 'clinic_id': None}
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return {'have_clinic': False, 'clinic_id': None}


def get_clinic_info(clinic_id):
    """Get clinic info by given clinic id.

    :param str clinic_id: Given clinic id
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM clinic_base WHERE clinic_id = '{clinic_id}'"
        cursor.execute(statement)
        for result in cursor:
            clinic_info = result
        return {
            'clinic_id': list(clinic_info)[0],
            'doc_id': list(clinic_info)[1],
            'doc_name': list(clinic_info)[2],
            'date': list(clinic_info)[3],
            'time_period': list(clinic_info)[4],
            'start_time': list(clinic_info)[5],
            'end_time': list(clinic_info)[6],
            'link': list(clinic_info)[7],
            'total_appointment': list(clinic_info)[8],
            'biggest_appointment_num': list(clinic_info)[9],
            'progress': list(clinic_info)[10]
        }
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return None
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return None


def update_clinic_status(clinic_id, **status_dict):
    """Update clinic status.

    :param str clinic_id: Registered clinic id
    :param dict status_dict: Clinic status dictionary, including start_time, end_time, link and progress
    """
    if status_dict['start_time'] is not None:
        try:
            statement = f"UPDATE clinic_base SET start_time = '{status_dict['start_time']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")
    if status_dict['end_time'] is not None:
        try:
            statement = f"UPDATE clinic_base SET end_time = '{status_dict['end_time']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")
    if status_dict['link'] is not None:
        try:
            statement = f"UPDATE clinic_base SET link = '{status_dict['link']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")
    if status_dict['total_appointment'] is not None:
        try:
            statement = f"UPDATE clinic_base SET total_appointment = '{status_dict['total_appointment']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")
    if status_dict['biggest_appointment_num'] is not None:
        try:
            statement = f"UPDATE clinic_base SET biggest_appointment_num = '{status_dict['biggest_appointment_num']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")
    if status_dict['progress'] is not None:
        try:
            statement = f"UPDATE clinic_base SET progress = '{status_dict['progress']}' WHERE clinic_id = '{clinic_id}'"
            cursor.execute(statement)
            connection.commit()
        except database.errors as error:
            print(f"Error retrieving entry from database: {error}")


def check_can_patient_make_appointment(patient_id, clinic_id):
    """Check if the patient can make appointment.

    :param str patient_id: Registered patient id
    :param str clinic_id: Registered clinic id
    :rtype: bool
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM appointment_base WHERE patient_id = '{patient_id}' AND clinic_id = '{clinic_id}'"
        cursor.execute(statement)
        for result in cursor:
            return False
        return True
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return False
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return False


def make_appointment(clinic_id, patient_id):
    """Make appointment.

    :param str clinic_id: Registered clinic id
    :param str patient_id: Registered patient id
    :rtype: int
    """
    patient_name = get_patient_info_by_id(patient_id)['name']
    clinic_info = get_clinic_info(clinic_id)
    if clinic_info is None:
        return 0
    appointment_num = clinic_info['biggest_appointment_num'] + 1
    total_appointment = clinic_info['total_appointment'] + 1
    try:
        statement = f"INSERT INTO appointment_base (clinic_id, patient_id, patient_name, appointment_num) VALUE ('{clinic_id}', '{patient_id}', '{patient_name}', {appointment_num})"
        cursor.execute(statement)
        connection.commit()
        update_clinic_status(clinic_id,
                             **{'start_time': None, 'end_time': None, 'link': None,
                                'progress': None,
                                'total_appointment': total_appointment,
                                'biggest_appointment_num': appointment_num})
        return appointment_num
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def cancel_appointment(patient_id, clinic_id):
    """Cancel appointment.

    :param str patient_id: Registered patient id
    :param str clinic_id: Registered clinic id
    """
    clinic_info = get_clinic_info(clinic_id)
    total_appointment = clinic_info['total_appointment'] - 1
    try:
        statement = f"DELETE FROM appointment_base WHERE patient_id = '{patient_id}' AND clinic_id = '{clinic_id}'"
        cursor.execute(statement)
        connection.commit()
        update_clinic_status(clinic_id,
                             **{'start_time': None, 'end_time': None, 'link': None,
                                'progress': None, 'biggest_appointment_num': None,
                                'total_appointment': total_appointment})
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def get_patient_appointment_with_clinic_id(patient_id, clinic_id):
    """Check patient appointment with clinic id.

    :param str patient_id: Registered patient id
    :param str clinic_id: Registered clinic id
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM appointment_base WHERE patient_id = '{patient_id}' AND clinic_id = '{clinic_id}'"
        cursor.execute(statement)
        for result in cursor:
            appointment_info = result
        return {
            'have_appointment': True,
            'order_id': appointment_info[0],
            'patient_id': appointment_info[1],
            'patient_name': appointment_info[2],
            'clinic_id': appointment_info[3],
            'appointment_num': appointment_info[4],
            'start_time': appointment_info[5],
            'end_time': appointment_info[6],
        }
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return {'have_appointment': False}
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return {'have_appointment': False}


def get_undone_patient_appointment(patient_id):
    """Check patient appointment with patient_id

    :param str patient_id: Registered patient id
    :rtype: dict
    """
    clinic_ids = []
    try:
        connection.autocommit = True
        statement = f"SELECT clinic_id FROM appointment_base WHERE patient_id = '{patient_id}' AND end_time is NULL"
        cursor.execute(statement)
        for result in cursor:
            clinic_ids.append(result[0])
        return clinic_ids
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return []
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return []


def doctor_login(doc_id, password):
    """Doctor login.

    :param str doc_id: Registered doctor id
    :param str password: Registered doctor password
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM doctor_base WHERE doc_id = '{doc_id}' AND password = '{password}'"
        cursor.execute(statement)
        for result in cursor:
            doctor_info = result
        return {
            'login': True,
            'doc_id': doctor_info[0],
            'doc_name': doctor_info[1],
            'department': doctor_info[2]
        }
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return {'login': False}
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return {'login': False}


def get_doctor_clinic_list(doc_id):
    """Get doctor clinics list.

    Will only shows the clinics from last week to next week.

    :param str doc_id: Registered doctor id
    :rtype: list
    """
    try:
        connection.autocommit = True
        statement = f"SELECT * FROM clinic_base WHERE doc_id = '{doc_id}' AND date >= '{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}' AND date <= '{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}'"
        cursor.execute(statement)
        clinics = []
        for result in cursor:
            clinics.append({
                'clinic_id': result[0],
                'doc_id': result[1],
                'doc_name': result[2],
                'date': result[3].strftime('%Y-%m-%d'),
                'time_period': result[4],
                'start_time': result[5].strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': result[6].strftime('%Y-%m-%d %H:%M:%S'),
                'link': result[7],
                'total_appointment': result[8],
                'biggest_appointment_num': result[9],
                'progress': result[10]
            })
        return clinics
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return []
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return []

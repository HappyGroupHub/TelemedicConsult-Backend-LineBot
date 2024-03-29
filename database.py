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


def register_patient(name, id, sex, birthday, blood_type, phone_number, address, height, weight, ice_contact,
                     ice_relation, ice_phone):
    try:
        statement = "INSERT INTO patient_base (name, id, sex, birthday, blood_type, phone_number, address, height, weight, ice_contact, ice_relation, ice_phone) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, id, sex, birthday, blood_type, phone_number, address, height, weight, ice_contact, ice_relation,
                  ice_phone)
        cursor.execute(statement, values)
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
        statement = "SELECT * FROM patient_base WHERE id = %s"
        cursor.execute(statement, (patient_id,))
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
        statement = "SELECT * FROM patient_base WHERE line_id = %s"
        cursor.execute(statement, (line_id,))
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
        statement = "UPDATE patient_base SET line_id = %s WHERE id = %s"
        values = (line_id, patient_id)
        cursor.execute(statement, values)
        connection.commit()
    except database.errors as error:
        print(f"Error updating entry in the database: {error}")


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
        statement = "UPDATE patient_base SET phone_number = %s, address = %s, height = %s, weight = %s, ice_contact = %s, ice_relation = %s, ice_phone = %s WHERE id = %s"
        values = (phone_number, address, height, weight, ice_contact, ice_relation, ice_phone, patient_id)
        cursor.execute(statement, values)
        connection.commit()
    except database.errors as error:
        print(f"Error updating entry in the database: {error}")


def is_line_registered(line_id):
    """Check if line id is registered.

    :param str line_id: Given line id
    :rtype: bool
    """
    try:
        connection.autocommit = True
        line_id = database.conversion.MySQLConverter().escape(line_id)
        statement = f"SELECT is_registered FROM line_registry WHERE line_id = %s"
        cursor.execute(statement, (line_id,))
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
        statement = "INSERT INTO line_registry (line_id, is_registered) VALUE (%s, %s)"
        values = (line_id, is_registered)
        cursor.execute(statement, values)
        connection.commit()
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")


def update_line_registry(line_id, is_registered):
    """Update line registry.

    :param str line_id: Registered line id
    :param bool is_registered: to registered or not
    """
    try:
        statement = "UPDATE line_registry SET is_registered = %s WHERE line_id = %s"
        values = (is_registered, line_id)
        cursor.execute(statement, values)
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
        statement = "SELECT clinic_id FROM clinic_base WHERE date = %s AND time_period = %s"
        cursor.execute(statement, (date, time_period))
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
        statement = "SELECT * FROM clinic_base WHERE clinic_id = %s"
        cursor.execute(statement, (clinic_id,))
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
    :param dict status_dict: Clinic status dictionary, including start_time, end_time, link, total_appointment, biggest_appointment_num, and progress
    """
    try:
        # Define a list of columns to update
        columns = ["start_time", "end_time", "link", "total_appointment", "biggest_appointment_num", "progress"]

        for column in columns:
            if column in status_dict and status_dict[column] is not None:
                statement = f"UPDATE clinic_base SET {column} = %s WHERE clinic_id = %s"
                cursor.execute(statement, (status_dict[column], clinic_id))

        connection.commit()
    except database.errors as error:
        print(f"Error updating clinic status in the database: {error}")


def check_can_patient_make_appointment(patient_id, clinic_id):
    """Check if the patient can make appointment.

    :param str patient_id: Registered patient id
    :param str clinic_id: Registered clinic id
    :rtype: bool
    """
    try:
        connection.autocommit = True
        statement = "SELECT * FROM appointment_base WHERE patient_id = %s AND clinic_id = %s"
        cursor.execute(statement, (patient_id, clinic_id))
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
    clinic_info = get_patient_ongoing_clinic_info(clinic_id)
    if clinic_info is None:
        return 0
    appointment_num = clinic_info['biggest_appointment_num'] + 1
    total_appointment = clinic_info['total_appointment'] + 1
    try:
        statement = "INSERT INTO appointment_base (clinic_id, patient_id, patient_name, appointment_num) VALUE (%s, %s, %s, %s)"
        values = (clinic_id, patient_id, patient_name, appointment_num)
        cursor.execute(statement, values)
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
    clinic_info = get_patient_ongoing_clinic_info(clinic_id)
    total_appointment = clinic_info['total_appointment'] - 1
    try:
        statement = "DELETE FROM appointment_base WHERE patient_id = %s AND clinic_id = %s"
        cursor.execute(statement, (patient_id, clinic_id))
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
        statement = "SELECT * FROM appointment_base WHERE patient_id = %s AND clinic_id = %s"
        cursor.execute(statement, (patient_id, clinic_id))
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


def get_patient_appointment_with_clinic_id_and_appointment_num(clinic_id, appointment_num):
    """Check patient appointment with clinic id.

    :param str clinic_id: Registered clinic id
    :param str appointment_num: Registered appointment number
    :rtype: dict
    """
    try:
        statement = "SELECT * FROM appointment_base WHERE clinic_id = %s AND appointment_num = %s"
        cursor.execute(statement, (clinic_id, appointment_num))
        result = cursor.fetchone()

        if result:
            return {
                'have_appointment': True,
                'order_id': result[0],
                'patient_id': result[1],
                'patient_name': result[2],
                'clinic_id': result[3],
                'appointment_num': result[4],
                'start_time': result[5],
                'end_time': result[6],
            }
        else:
            return {'have_appointment': False}
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return {'have_appointment': False}


def get_patient_undone_clinic_ids(patient_id):
    """Check patient undone appointment with clinic id.

    :param str patient_id: Registered patient id
    :rtype: list
    """
    try:
        statement = "SELECT clinic_id FROM appointment_base WHERE patient_id = %s AND end_time IS NULL"
        cursor.execute(statement, (patient_id,))
        clinic_ids = [result[0] for result in cursor.fetchall()]
        return clinic_ids
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return []


def get_patient_undone_appointment(clinic_id):
    """Check if a patient has an undone appointment with a specific clinic ID.

    :param str clinic_id: Clinic ID
    :return: Dictionary with appointment information or {'have_appointment': False} if no matching result
    :rtype: dict
    """
    try:
        statement = "SELECT * FROM appointment_base WHERE clinic_id = %s AND end_time IS NULL"
        cursor.execute(statement, (clinic_id,))
        appointment_info = cursor.fetchone()

        if appointment_info:
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
        else:
            return {'have_appointment': False}

    except database.errors as error:
        print(f"Error retrieving entry from the database: {error}")
        return {'have_appointment': False}


def get_patient_ongoing_appointment(patient_id):
    """Get ongoing appointment of the patient with patient id.

    :param str patient_id: Registered patient ID
    :return: Dictionary containing the clinic ID and appointment number of the ongoing appointment, or None if there's no ongoing appointment
    :rtype: dict or None
    """
    clinic_ids = get_patient_undone_clinic_ids(patient_id)

    for clinic_id in clinic_ids:
        try:
            statement = "SELECT start_time FROM clinic_base WHERE clinic_id = %s"
            cursor.execute(statement, (clinic_id,))
            start_time = cursor.fetchone()

            if start_time is not None:
                appointment_info = get_patient_appointment_with_clinic_id(patient_id, clinic_id)
                return {
                    'clinic_id': clinic_id,
                    'appointment_num': appointment_info['appointment_num']
                }
        except database.errors as error:
            print(f"Error retrieving entry from the database: {error}")

    return None


def get_patient_ongoing_clinic_info(clinic_id):
    """Get information about an ongoing clinic by clinic ID.

    :param str clinic_id: Clinic ID
    :return: Dictionary containing clinic information or None if no ongoing clinic found
    :rtype: dict or None
    """
    try:
        statement = "SELECT * FROM clinic_base WHERE clinic_id = %s AND end_time IS NULL"
        cursor.execute(statement, (clinic_id,))
        ongoing_clinic_info = cursor.fetchone()

        if ongoing_clinic_info:
            return {
                'clinic_id': ongoing_clinic_info[0],
                'doc_id': ongoing_clinic_info[1],
                'doc_name': ongoing_clinic_info[2],
                'date': ongoing_clinic_info[3],
                'time_period': ongoing_clinic_info[4],
                'start_time': ongoing_clinic_info[5],
                'end_time': ongoing_clinic_info[6],
                'link': ongoing_clinic_info[7],
                'total_appointment': ongoing_clinic_info[8],
                'biggest_appointment_num': ongoing_clinic_info[9],
                'progress': ongoing_clinic_info[10]
            }
        else:
            return None

    except database.errors as error:
        print(f"Error retrieving entry from the database: {error}")
        return None


def get_unstarted_patient_reservation_appointments(patient_id):
    """Get a list of patient's unstarted reservation appointments.

    :param str patient_id: Registered patient ID
    :return: List of dictionaries containing appointment information or an empty list if no matching results
    :rtype: list
    """
    reservation_list = []
    try:
        statement = "SELECT * FROM appointment_base WHERE patient_id = %s AND end_time IS NULL"
        cursor.execute(statement, (patient_id,))
        for appointment_info in cursor:
            reservation_list.append({
                'have_appointment': True,
                'order_id': appointment_info[0],
                'patient_id': appointment_info[1],
                'patient_name': appointment_info[2],
                'clinic_id': appointment_info[3],
                'appointment_num': appointment_info[4],
                'start_time': appointment_info[5],
                'end_time': appointment_info[6],
            })
        return reservation_list
    except database.errors as error:
        print(f"Error retrieving entry from the database: {error}")
        return []


def doctor_login(doc_id, password):
    """Doctor login.

    :param str doc_id: Registered doctor id
    :param str password: Registered doctor password
    :rtype: dict
    """
    try:
        connection.autocommit = True
        statement = "SELECT * FROM doctor_base WHERE doc_id = %s AND password = %s"
        cursor.execute(statement, (doc_id, password))
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
    clinics = []
    try:
        connection.autocommit = True
        statement = "SELECT * FROM clinic_base WHERE doc_id = %s AND date >= %s AND date <= %s"
        cursor.execute(statement, (doc_id, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                                   (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')))
        for result in cursor:
            clinics.append({
                'clinic_id': result[0],
                'doc_id': result[1],
                'doc_name': result[2],
                'date': result[3].strftime('%Y-%m-%d'),
                'time_period': result[4],
                'start_time': result[5],
                'end_time': result[6],
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


def get_patients_by_clinic_id(clinic_id):
    """Get patients list by clinic id.

    :param str clinic_id: Registered clinic id
    :rtype: list
    """
    patients = []
    try:
        connection.autocommit = True
        statement = "SELECT patient_id, patient_name, appointment_num FROM appointment_base WHERE clinic_id = %s ORDER BY appointment_num ASC"
        cursor.execute(statement, (clinic_id,))
        for result in cursor:
            patients.append({
                'patient_id': result[0],
                'patient_name': result[1],
                'appointment_num': result[2]
            })
        return patients
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return []
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return []


def update_appointment_start_time_to_now(clinic_id, appointment_num):
    """Update appointment start time to now.

    :param str clinic_id: Registered clinic id
    :param str appointment_num: Registered appointment number
    """
    try:
        statement = "UPDATE appointment_base SET start_time = %s WHERE clinic_id = %s AND appointment_num = %s"
        values = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), clinic_id, appointment_num)
        cursor.execute(statement, values)
        connection.commit()
    except (TypeError, UnboundLocalError):
        print("Error updating entry from database, no matching results")
    except database.errors as error:
        print(f"Error updating entry from database: {error}")


def update_appointment_end_time_to_now(clinic_id, appointment_num):
    """Update appointment end time to now.

    :param str clinic_id: Registered clinic id
    :param str appointment_num: Registered appointment number
    """
    try:
        statement = "UPDATE appointment_base SET end_time = %s WHERE clinic_id = %s AND appointment_num = %s"
        values = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), clinic_id, appointment_num)
        cursor.execute(statement, values)
        connection.commit()
    except (TypeError, UnboundLocalError):
        print("Error updating entry from database, no matching results")
    except database.errors as error:
        print(f"Error updating entry from database: {error}")


def clear_appointment_start_time_end_time(clinic_id, appointment_num):
    """Set appointment start time and end time to NULL.

    :param str clinic_id: Registered clinic id
    :param str appointment_num: Registered appointment number
    """
    try:
        statement = "UPDATE appointment_base SET start_time = NULL, end_time = NULL WHERE clinic_id = %s AND appointment_num = %s"
        values = (clinic_id, appointment_num)
        cursor.execute(statement, values)
        connection.commit()
    except (TypeError, UnboundLocalError):
        print("Error updating entry from database, no matching results")
    except database.errors as error:
        print(f"Error updating entry from database: {error}")

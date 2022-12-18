"""This python file will handle all the database things."""

import sys

import mysql.connector as database
import yaml
from yaml import SafeLoader

try:
    with open('config.yml', 'r', encoding="utf8") as f:
        config = yaml.load(f, Loader=SafeLoader)
except FileNotFoundError:
    print("Config file not found, please create a config.yml file")
    sys.exit()

hostname = config['Database']['hostname']
db_name = config['Database']['db_name']
username = config['Database']['username']
password = config['Database']['password']

connection = database.connect(
    user=username,
    password=password,
    host=hostname,
    database=db_name
)

cursor = connection.cursor()


def get_patient_info_by_id(patient_id):
    """Get patient info by patient id.

    :param str patient_id: Registered patient id
    :rtype: dict
    """
    try:
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


def is_line_registered(line_id):
    """Check if line id is registered.

    :param str line_id: Given line id
    :rtype: bool
    """
    try:
        statement = f"SELECT is_registered FROM line_registry WHERE line_id = '{line_id}'"
        cursor.execute(statement)
        for result in cursor:
            is_registered = result
        return list(is_registered)[0]
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return "Error"
    except database.errors as error:
        print(f"Error retrieving entry from database: {error}")
        return None


def create_line_registry(line_id, is_registered):
    """Create line registry by given line id.

    This function will create a new line registry data by given line id.
    Only use this function when the given line id is not registered in line_registry table.
    And the is_registered parameter should be false by default.

    :param str line_id: Given line id
    :param bool is_registered: to registered or not (should be false by default)
    """
    try:
        statement = f"INSERT INTO line_registry(line_id, is_registered) VALUE ('{line_id}', {is_registered})"
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

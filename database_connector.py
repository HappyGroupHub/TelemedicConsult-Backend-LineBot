import mysql.connector as database
import yaml
from yaml import SafeLoader

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

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


def get_patient_info(patient_id):
    try:
        statement = "SELECT * FROM patient_base WHERE id = '{}'".format(patient_id)
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
    except database.errors as e:
        print("Error retrieving entry from database: {}".format(e))


def update_patient_line_id(patient_id, line_id):
    try:
        statement = "UPDATE patient_base SET line_id = '{}' WHERE id = '{}'".format(line_id, patient_id)
        cursor.execute(statement)
        connection.commit()
    except database.errors as e:
        print("Error retrieving entry from database: {}".format(e))


def is_line_registered(line_id):
    try:
        statement = "SELECT is_registered FROM line_registry WHERE line_id = '{}'".format(line_id)
        cursor.execute(statement)
        for result in cursor:
            is_registered = result
        return list(is_registered)[0]
    except (TypeError, UnboundLocalError):
        print("Error retrieving entry from database, no matching results")
        return "Error"


def create_line_registry(line_id, is_registered):
    try:
        statement = "INSERT INTO line_registry(line_id, is_registered) VALUE ('{}', {})".format(line_id, is_registered)
        cursor.execute(statement)
        connection.commit()
    except database.errors as e:
        print("Error retrieving entry from database: {}".format(e))


def update_line_registry(line_id, is_registered):
    try:
        statement = "UPDATE line_registry SET is_registered = {} WHERE line_id = '{}'".format(is_registered, line_id)
        cursor.execute(statement)
        connection.commit()
    except database.errors as e:
        print("Error retrieving entry from database: {}".format(e))

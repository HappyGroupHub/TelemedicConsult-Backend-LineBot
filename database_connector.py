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


def get_patient_info(patient_id, patient_data_type):
    try:
        statement = "SELECT {} FROM patient_base WHERE id = '{}'".format(patient_data_type, patient_id)
        cursor.execute(statement)
        for result in cursor:
            patient_info = result
        return list(patient_info)[0]
    except database.errors as e:
        print("Error retrieving entry from database: {}".format(e))


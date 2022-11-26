import sys
import mariadb
import yaml
from yaml import SafeLoader


with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=SafeLoader)

hostname = config['Database']['hostname']
db_name = config['Database']['db_name']
port = config['Database']['port']
username = config['Database']['username']
password = config['Database']['password']

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user=username,
        password=password,
        host=hostname,
        port=int(port),
        database=db_name
    )
    # Get Cursor
    cur = conn.cursor()
    cur.execute("SELECT name FROM patient_base")
    for (name) in cur:
        print(name)

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)



"""This python file will handle some extra functions."""

import datetime
import sys

import yaml
from yaml import SafeLoader


def read_config():
    """Read config file.

    Check if config file exists, if not, create one.
    if exists, read config file and return config with dict type.

    :rtype: dict
    """
    try:
        with open('config.yml', 'r', encoding="utf8") as f:
            data = yaml.load(f, Loader=SafeLoader)
            config = {
                'line_channel_secret': data['Line']['channel_secret'],
                'line_channel_access_token': data['Line']['channel_access_token'],
                'db_hostname': data['Database']['hostname'],
                'db_name': data['Database']['db_name'],
                'db_username': data['Database']['username'],
                'db_password': data['Database']['password'],
                'webhook_base_extension': data['Webhook_with_web']['base_extension']
            }
            return config
    except FileNotFoundError:
        print("Config file not found, create one by default.\nPlease finish filling config.yml")
        with open('config.yml', 'w', encoding="utf8") as f:
            f.write(
                "Line:\n  channel_access_token: ''\n  channel_secret: ''\n"
                "Database:\n  hostname: ''\n  db_name: ''\n  username: ''\n  password: ''\n"
                "Webhook_with_web:\n  base_extension: ''")
        sys.exit()
    except (KeyError, TypeError):
        print("An error occurred while reading config.yml, please check if the file is corrected filled.\n"
              "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()


def is_id_legal(id_number):
    """Check if id number is legal.

    :param str id_number: Given id number
    :rtype: bool
    """
    try:
        alpha_table = {'A': 1, 'B': 10, 'C': 19, 'D': 28, 'E': 37, 'F': 46,
                       'G': 55, 'H': 64, 'I': 39, 'J': 73, 'K': 82, 'L': 2, 'M': 11,
                       'N': 20, 'O': 48, 'P': 29, 'Q': 38, 'R': 47, 'S': 56, 'T': 65,
                       'U': 74, 'V': 83, 'W': 21, 'X': 3, 'Y': 12, 'Z': 30}

        id_sum = alpha_table[id_number[0]] + int(id_number[1]) * 8 + int(id_number[2]) * 7 + int(
            id_number[3]) * 6 + int(
            id_number[4]) * 5 + int(id_number[5]) * 4 + int(
            id_number[6]) * 3 + int(id_number[7]) * 2 + int(id_number[8]) * 1 + int(id_number[9])
        return bool(id_sum % 10 == 0)
    except (KeyError, ValueError, IndexError):
        return False


def is_date(date):
    """Check if date is legal.

    :param str date: Given date
    :rtype: bool
    """
    try:
        datetime.datetime.strptime(date, '%Y/%m/%d')
        return True
    except ValueError:
        return False

import datetime


def is_id_legal(id_number):
    try:
        alpha_table = {'A': 1, 'B': 10, 'C': 19, 'D': 28, 'E': 37, 'F': 46,
                       'G': 55, 'H': 64, 'I': 39, 'J': 73, 'K': 82, 'L': 2, 'M': 11,
                       'N': 20, 'O': 48, 'P': 29, 'Q': 38, 'R': 47, 'S': 56, 'T': 65,
                       'U': 74, 'V': 83, 'W': 21, 'X': 3, 'Y': 12, 'Z': 30}

        sum = alpha_table[id_number[0]] + int(id_number[1]) * 8 + int(id_number[2]) * 7 + int(id_number[3]) * 6 + int(
            id_number[4]) * 5 + int(id_number[5]) * 4 + int(
            id_number[6]) * 3 + int(id_number[7]) * 2 + int(id_number[8]) * 1 + int(id_number[9])
        if sum % 10 == 0:
            return True
        else:
            return False
    except KeyError:
        return False


def is_date(date):
    try:
        datetime.datetime.strptime(date, '%Y/%m/%d')
        return True
    except ValueError:
        return False

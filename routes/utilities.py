import re
from datetime import datetime


def email_string_checker(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(regex, email):
        return True
    else:
        return False
    

def flag_checker(flag):
    regex = r'linuxlab\{+[A-Za-z0-9_]+\}'

    if re.fullmatch(regex, flag):
        return True
    else:
        return False

  
def flag_format_strip(flag):
  
  first_regex = r'[\{]+[A-Za-z0-9\_\-]+[\}]'
  second_regex = r'[^\{]+[A-Za-z0-9\_\-]+[^\}]'

  first_match = re.search(first_regex, flag)

  if first_match:
    half_strip = flag[first_match.start():first_match.end()]
    
    second_match = re.search(second_regex, half_strip)
    
    if half_strip:
        return half_strip[second_match.start():second_match.end()]
    else:
        return None
  else:
      return None


def time_length_formatter(value):
    str_list = list(str(value))
    str_value = ""
    max_length = 6

    if len(str_list) <= max_length:
        for i in range(0, len(str_list), 2):
            str_value += str_list[i]
            
            if i + 1 < len(str_list):
                str_value += str_list[i+1]

            if i + 2 < len(str_list):
                str_value += ":"
    else:
        for i in range(0, 6, 2):
            str_value += str_list[i]
            
            if i + 1 < max_length:
                str_value += str_list[i+1]

            if i + 2 < max_length:
                str_value += ":"
    return str_value


def parse_time_duration(value):
    
    if len(value) > 3 and len(value) < 7:
        old_value = value
        new_value = f"00:{old_value}"

        return list(map(lambda x: int(x), new_value.split(":")))
    elif len(value) < 3:
        old_value = value
        new_value = f"00:00:{old_value}"

        return list(map(lambda x: int(x), new_value.split(":")))
    else:
        return list(map(lambda x: int(x), value.split(":")))


def convert_to_timestamp(timestamp_string, format_string):
    datetime_obj = datetime.strptime(timestamp_string, format_string)
    return datetime_obj


def convert_timestamp_str(date):
        
        format_string = "%Y-%m-%d %H:%M:%S"
        datetime_obj = convert_to_timestamp(date, format_string)
        new_timestamp = datetime_obj.timestamp()

        milisecond_timestamp = int(round(new_timestamp * 1000))
        return milisecond_timestamp

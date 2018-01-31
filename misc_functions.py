from datetime import date

def convert_list_to_date(list):
    new_list = []
    for item in list:
        split = item.split('/')
        day = int(split[0])
        month = int(split[1])
        year = int(split[2])
        d = date(year, month, day)
        new_list.append(d)
    return new_list


def convert_to_date(entry):

    split = entry.split('-')
    day = int(split[0])
    month = int(split[1])
    year = int(split[2])
    d = date(year, month, day)
    return d


def fix_dates(datum_list):
    new_list = []
    for line in datum_list:
        line_new = str(line)
        line_new = line_new[:-3]
        line_new = datetime.fromtimestamp(int(line_new)).strftime('%Y-%m-%d')
        new_list.append(line_new)
    new_list = convert_to_date(new_list)
    return new_list

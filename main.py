import csv
import json
import secrets
import string
from datetime import datetime
from dateutil.parser import parse
import os
import re
import sys


with open("config/customers.json", "r") as file:
    try:
        customer = sys.argv[2]
        customers = json.load(file)[customer]
    except IndexError:
        print('Customer not informed.')
        exit(1)
    except KeyError:
        print(f'Customer {customer} not found on customers config file.')
        exit(1)

with open("config/headers.json", "r") as file:
    try:
        version = customers['version']
        headers = json.load(file)[version]
    except IndexError:
        print('Version not informed.')
        exit(1)
    except KeyError:
        print(f'Version {version} not found on headers config file.')
        exit(1)


with open("config/mappings.json", "r") as file:
    try:
        customer = sys.argv[2]
        mappings = json.load(file)[customer]
    except IndexError:
        print('Customer not informed.')
        exit(1)
    except KeyError:
        print(f'Customer {customer} not found on mappings config file.')
        exit(1)

def search_files(filter):
    search_path = customers['input']
    files_found = []

    for dirpath, dirnames, filenames in os.walk(search_path):
        for filename in [file for file in filenames if re.search(filter, file)]:
            files_found.append(os.path.join(dirpath, filename))

    return files_found


def generate_line_item_files(file_path, writer_aggregated):
    with open(file_path, newline='') as input_file:
        output_path = prepare_output_path(file_path)

        reader = csv.DictReader(input_file)

        writer_lqa = get_writer(f'{output_path}/line_items_lqa.csv')
        writer_qa = get_writer(f'{output_path}/line_items_qa.csv')

        writer_lqa.writerow(headers['line-items'])
        writer_qa.writerow(headers['line-items'])

        for row in reader:
            line_item_lqa = get_line_item_lqa(row)
            line_item_qa = get_line_item_qa(row)

            writer_lqa.writerow(line_item_lqa)
            writer_qa.writerow(line_item_qa)
            writer_aggregated.writerows([line_item_lqa, line_item_qa])


def generate_user_files(file_path, writer_aggregated):
    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        output_path = prepare_output_path(file_path)
        groups = customers['groups']
        users_per_test = customers['users_per_test']

        for row in reader:
            slug = map_field(row, 'slug')

            for group in groups:
                path_lqa = f'{output_path}/{group}/LQA'
                path_qa = f'{output_path}/{group}/QA'

                create_directories(path_lqa)
                create_directories(path_qa)

                writer_live = get_writer(f'{path_lqa}/{slug}-users_per_test.csv')
                writer_qa = get_writer(f'{path_qa}/{slug}-users_per_test.csv')

                writer_live.writerow(headers['users'])
                writer_qa.writerow(headers['users'])

                for index in range(1, users_per_test + 1):
                    user_live = get_user(slug, group, index)
                    user_qa = get_user(f'{slug}_QA', group, index)

                    writer_live.writerow(user_live)
                    writer_qa.writerow(user_qa)
                    writer_aggregated.writerows([user_live, user_qa])


def map_field(row, field):
    real_field = mappings[field]

    return row[real_field]


def get_line_item_qa(row):
    return [
        encode_uri(f'{customers["uri"]}-{map_field(row, "slug")}_QA'),
        f'{map_field(row, "label")} (QA)',
        f'{map_field(row, "slug")}_QA',
        None,
        None,
        0
    ]


def get_line_item_lqa(row):
    return [
        encode_uri(f'{customers["uri"]}-{map_field(row, "slug")}'),
        map_field(row, "label"),
        map_field(row, "slug"),
        convert_date(map_field(row, "startTimestamp")),
        convert_date(map_field(row, "endTimestamp")),
        1,
    ]


def encode_uri(uri):
    uri = re.sub("_(\d)_", r"-\1-", uri)
    uri = re.sub("-(\d)_", r"-\1-", uri)

    return uri


def get_user(slug, group, index):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(customers['password_size']))
    username = f'{slug}_{group}_{index}'

    user = [
        username,
        password
    ]

    if customers['version'] == "1.x":
        user.append(slug)

    return user


def convert_date(date):
    if str(date).isnumeric():
        return date

    return int(datetime.timestamp(parse(date)))


def create_directories(file_path):
    try:
        os.makedirs(file_path)
    except OSError:
        print("Creation of the directory %s failed" % file_path)
    else:
        print("Successfully created the directory %s " % file_path)


def prepare_output_path(file_path):
    output_path = os.path.dirname(os.path.realpath(file_path)).replace('input', 'output')

    try:
        os.makedirs(output_path)
    except OSError:
        print("Creation of the directory %s failed" % output_path)
    else:
        print("Successfully created the directory %s " % output_path)

    return output_path


def get_writer(file_path):
    output_file = open(file_path, 'w')
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    return writer


def generate_line_items():
    line_item_files = search_files(customers['line-item-filter'])
    aggregated_writer = get_writer(customers["aggregated-line-item-file"])
    aggregated_writer.writerow(headers['line-items'])

    print('Files to be processed:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_line_item_files(file, aggregated_writer)


def generate_users():
    line_item_files = search_files(customers['line-item-filter'])
    aggregated_writer = get_writer(customers['aggregated-user-file'])
    aggregated_writer.writerow(headers['users'])

    print('Files to be processed:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_user_files(file, aggregated_writer)


def check_line_items():
    slugs = get_slugs_from_file(customers['aggregated-line-item-file'])

    with open(customers['aggregated-user-file'], newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            try:
                slugs.index(row['slug'])
            except ValueError:
                print(f'User {row} have non existing slug')


def get_slugs_from_file(file_path):
    slugs = []

    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            slugs.append(row['slug'])

    return slugs


def aggregate_real_users():
    user_files = search_files(customers['user-filter'])
    aggregated_writer = get_writer('output/nsa/real_users_aggregated.csv')
    aggregated_writer.writerow(headers['users'])

    for file_path in user_files:
        with open(file_path, newline='') as input_file:
            reader = csv.DictReader(input_file)

            for row in reader:
                if 'groupid' in row:
                    row.pop('groupid')

                row = sanitize_row(row)

                aggregated_writer.writerow(row.values())


def sanitize_row(row):
    row = {k: v.strip() for k, v in row.items()}

    return row


if __name__ == '__main__':
    action = sys.argv[1]

    if action == 'line-items:generate':
        generate_line_items()
    elif action == 'users:generate':
        generate_users()
    elif action == 'users:check_line_items':
        check_line_items()
    elif action == 'users:aggregate_real_users':
        aggregate_real_users()
    else:
        print('Invalid operation')

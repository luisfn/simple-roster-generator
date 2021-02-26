import csv
import secrets
import string
from datetime import datetime
from dateutil.parser import parse
import os
import re

from cli import selector
from config import config


def search_files(filter):
    search_path = customers.get('input')
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

        writer_lqa.writerow(headers.get('line-items'))
        writer_qa.writerow(headers.get('line-items'))

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
        groups = customers.get('groups')
        users_per_test = customers.get('users-per-test')

        for row in reader:
            slug = map_field(row, 'slug')

            for group in groups:
                path_lqa = f'{output_path}/{group}/LQA'
                path_qa = f'{output_path}/{group}/QA'

                create_directories(path_lqa)
                create_directories(path_qa)

                writer_live = get_writer(f'{path_lqa}/{slug}-users.csv')
                writer_qa = get_writer(f'{path_qa}/{slug}-users.csv')

                writer_live.writerow(headers.get('users'))
                writer_qa.writerow(headers.get('users'))

                for index in range(1, users_per_test + 1):
                    user_live = get_user(slug, group, index)
                    user_qa = get_user(f'{slug}_QA', group, index)

                    writer_live.writerow(user_live)
                    writer_qa.writerow(user_qa)
                    writer_aggregated.writerows([user_live, user_qa])


def map_field(row, field):
    real_field = mappings.get(field)

    return row[real_field]


def get_line_item_qa(row):
    line_item = [
        encode_uri(f'{customers.get("uri")}-{map_field(row, "slug")}_QA'),
        f'{map_field(row, "label")} (QA)',
        f'{map_field(row, "slug")}_QA',
        None,
        None,
        0
    ]

    if version == "1.x":
        line_item.append(customers.get("infrastructure"))

    return line_item


def get_line_item_lqa(row):
    line_item = [
        encode_uri(f'{customers.get("uri")}-{map_field(row, "slug")}'),
        map_field(row, "label"),
        map_field(row, "slug"),
        convert_date(map_field(row, "startTimestamp")),
        convert_date(map_field(row, "endTimestamp")),
        1,
    ]

    if version == "1.x":
        line_item.append(customers.get("infrastructure"))

    return line_item


def encode_uri(uri):
    uri = re.sub("_(\d)_", r"-\1-", uri)
    uri = re.sub("-(\d)_", r"-\1-", uri)

    return uri


def get_user(slug, group, index):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(customers.get('password-size')))
    username = f'{slug}_{group}_{index}'

    user = [
        username,
        password
    ]

    if version == "1.x":
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


def create_line_items():
    line_item_files = search_files(customers.get('line-item-filter'))
    aggregated_writer = get_writer(customers.get("aggregated-line-item-file"))
    aggregated_writer.writerow(headers.get('line-items'))

    print('Files to be processed:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_line_item_files(file, aggregated_writer)


def create_users():
    line_item_files = search_files(customers.get('line-item-filter'))
    aggregated_writer = get_writer(customers.get('aggregated-user-file'))
    aggregated_writer.writerow(headers.get('users'))

    print('Files to be processed:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_user_files(file, aggregated_writer)


def check_user_slugs():
    slugs = get_slugs_from_file(customers.get('aggregated-line-item-file'))
    errors = 0

    with open(customers.get('aggregated-user-file'), newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            try:
                slugs.index(row['slug'])
            except ValueError:
                errors += 1
                print(f'User {row} have non existing slug')

    if errors == 0:
        print('No errors found')


def get_slugs_from_file(file_path):
    slugs = []

    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            slugs.append(row['slug'])

    return slugs


def aggregate_real_users():
    user_files = search_files(customers.get('user-filter'))
    aggregated_writer = get_writer(customers.get('aggregated-real-user-file'))
    aggregated_writer.writerow(headers.get('users'))

    print('Files to be processed:', *user_files, sep='\n- ')

    for file_path in user_files:
        with open(file_path, newline='') as input_file:
            print(f'Processing {file_path} ...')

            reader = csv.DictReader(input_file)

            for row in reader:
                if 'groupid' in row:
                    row.pop('groupid')

                row = sanitize_row(row)

                aggregated_writer.writerow(row.values())


def check_duplicated_usernames():
    user_files = search_files(customers.get('user-filter'))

    seen = {}
    duplicated_usersnames = []

    for file_path in user_files:
        with open(file_path, newline='') as input_file:
            reader = csv.DictReader(input_file)

            for row in reader:
                values = list(row.values())

                username = values[0]
                if username not in seen:
                    seen[username] = 1
                else:
                    if seen[username] == 1:
                        duplicated_usersnames.append(username)
                    seen[username] += 1

    for duplication in duplicated_usersnames:
        print(duplication)


def sanitize_row(row):
    row = {k: v.strip() for k, v in row.items()}

    return row


if __name__ == '__main__':
    options = selector.options()
    action = options.get('action')
    customer = options.get('customer')

    customers = config.get('customers').get(customer)
    version = customers.get('version')
    headers = config.get('headers').get(version)
    mappings = config.get('mappings').get(customer)

    if action == selector.CREATE_LINE_ITEMS:
        create_line_items()
    elif action == selector.CREATE_USERS:
        create_users()
    elif action == selector.CHECK_USER_SLUGS:
        check_user_slugs()
    elif action == selector.AGGREGATE_REAL_USERS:
        aggregate_real_users()
    elif action == selector.CHECK_DUPLICATED_USERNAMES:
        check_duplicated_usernames()
    else:
        print('Invalid operation')

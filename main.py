import csv
import os
import re
import secrets
import string
from datetime import datetime

from dateutil.parser import parse
from rich.console import Console

from cli import selector
from config import config

console = Console()


def search_files(filter):
    search_path = customers.get('input')
    files_found = []

    for dirpath, dirnames, filenames in os.walk(search_path):
        for filename in [file for file in filenames if re.search(filter, file)]:
            files_found.append(os.path.join(dirpath, filename))

    return files_found


def generate_line_item_files(file_path, writer_aggregated):
    with open(file_path, newline='') as input_file:
        output_path = get_directory(file_path).replace('input', 'output')
        create_directories(output_path)

        reader = csv.DictReader(input_file)

        writer_lqa = get_writer(f'{output_path}/line_items_lqa.csv')
        writer_qa = get_writer(f'{output_path}/line_items_qa.csv')

        line_item_headers = headers.get('line-items')

        if not customers.get('line-item-group-id-enabled'):
            line_item_headers.remove('groupId')

        writer_lqa.writerow(line_item_headers)
        writer_qa.writerow(line_item_headers)

        for row in reader:
            line_item_lqa = get_line_item_lqa(row)
            line_item_qa = get_line_item_qa(row)

            writer_lqa.writerow(line_item_lqa)
            writer_qa.writerow(line_item_qa)
            writer_aggregated.writerows([line_item_lqa, line_item_qa])


def generate_user_files(file_path, aggregated_user_writer, aggregated_assignment_writer):
    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        output_path = customers.get('split-users-directory')
        create_directories(output_path)

        groups = customers.get('groups')
        users_per_test = customers.get('users-per-test')

        for row in reader:
            slug = map_field(row, 'line-items.slug')

            for group in groups:
                path_lqa = f'{output_path}/{group}/LQA'
                path_qa = f'{output_path}/{group}/QA'

                create_directories(path_lqa)
                create_directories(path_qa)

                user_file_live = f'{path_lqa}/{slug}-users.csv'
                user_file_qa = f'{path_qa}/{slug}-users.csv'

                writer_live = get_writer(user_file_live)
                writer_qa = get_writer(user_file_qa)

                writer_live.writerow(headers.get('users'))
                writer_qa.writerow(headers.get('users'))

                group_index = 1

                for index in range(1, users_per_test + 1):
                    user_live = get_user(slug, group, index, group_index)
                    user_qa = get_user(f'{slug}_QA', group, index, group_index)

                    writer_live.writerow(user_live)
                    writer_qa.writerow(user_qa)
                    aggregated_user_writer.writerows([user_live, user_qa])

                    if version == '2.x':
                        aggregated_assignment_writer.writerow([
                            f'{slug}_{group}_{index}',
                            slug
                        ])

                        aggregated_assignment_writer.writerow([
                            f'{slug}_QA_{group}_{index}',
                            f'{slug}_QA'
                        ])

                    # TODO make it dynamic, based on the users x groups
                    if index % 20 == 0:
                        group_index += 1

                console.print(f'- Generated {user_file_live} - with {users_per_test} users')
                console.print(f'- Generated {user_file_qa} - with {users_per_test} users')


def map_field(row, path):
    field = mappings
    keys = path.split('.')

    for key in keys:
        field = field.get(key)

    return row.get(field)


def get_line_item_qa(row):
    if not customers.get("uri"):
        uri = map_field(row, "line-items.slug")
    else:
        uri = encode_uri(f'{customers.get("uri")}{map_field(row, "line-items.slug")}_QA')

    line_item = [
        uri,
        f'{map_field(row, "line-items.label")}_QA',
        f'{map_field(row, "line-items.slug")}_QA',
        None,
        None,
        0
    ]

    if version == "1.x":
        line_item.append(customers.get("infrastructure"))

    if customers.get('line-item-group-id-enabled'):
        group_id = f'{map_field(row, "line-items.groupId")}_QA'
        line_item.append(group_id)

    return line_item


def get_line_item_lqa(row):
    if not customers.get("uri"):
        uri = map_field(row, "line-items.slug")
    else:
        uri = encode_uri(f'{customers.get("uri")}{map_field(row, "line-items.slug")}')

    line_item = [
        uri,
        map_field(row, "line-items.label"),
        map_field(row, "line-items.slug"),
        convert_date(map_field(row, "line-items.startTimestamp")),
        convert_date(map_field(row, "line-items.endTimestamp")),
        convert_date(map_field(row, "line-items.maxAttempts")),
    ]

    if version == "1.x":
        line_item.append(customers.get("infrastructure"))

    if customers.get('line-item-group-id-enabled'):
        group_id = f'{map_field(row, "line-items.groupId")}'
        line_item.append(group_id)

    return line_item


def encode_uri(uri):
    uri = re.sub("_(\d)_", r"-\1-", uri)
    uri = re.sub("-(\d)_", r"-\1-", uri)
    uri = re.sub("_(\d)-", r"-\1-", uri)

    return uri


def get_user(slug, group, index, group_index):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(customers.get('password-size')))
    username = f'{slug}_{group}_{index}'

    user = [
        username,
        password
    ]

    if version == "1.x":
        user.append(slug)

    if customers.get('user-group-id-enabled'):
        if customers.get('default-user-group-id'):
            user.append(customers.get('default-user-group-id'))
        else:
            group_id = f'{slug}_{str(group_index).zfill(4)}'
            user.append(group_id)

    return user


def convert_date(date):
    if date == "":
        return None

    if str(date).isnumeric():
        return date

    return int(datetime.timestamp(parse(date)))


def create_directories(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        console.print("Creation of the directory %s failed" % path)


def get_directory(file_path):
    output_path = os.path.dirname(os.path.realpath(file_path))

    return output_path


def get_writer(file_path):
    directory = os.path.dirname(os.path.realpath(file_path))
    create_directories(directory)

    output_file = open(file_path, 'w')
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    return writer


def create_line_items():
    line_item_files = search_files(customers.get('line-item-filter'))
    aggregated_writer = get_writer(customers.get("aggregated-line-item-file"))
    aggregated_writer.writerow(headers.get('line-items'))

    console.print('Line Items will be generated based on following files:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_line_item_files(file, aggregated_writer)


def create_users():
    line_item_files = search_files(customers.get('line-item-filter'))

    aggregated_user_writer = get_writer(customers.get('aggregated-user-file'))
    aggregated_assignment_writer = get_writer(customers.get('aggregated-assignment-file'))

    aggregated_user_writer.writerow(headers.get('users'))
    aggregated_assignment_writer.writerow(headers.get('assignments'))

    console.print('Users will be generated based on following files:', *line_item_files, sep='\n- ')

    for file in line_item_files:
        generate_user_files(file, aggregated_user_writer, aggregated_assignment_writer)


def check_user_slugs(user_type):
    file_path = user_file_path(user_type)

    slugs = get_slugs_from_file(customers.get('aggregated-line-item-file'))
    errors = False

    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            try:
                slug = row['slug'] if version == '1.x' else row['lineItemSlug']
                slugs.index(slug)
            except ValueError:
                errors = True
                console.print(f'User {row} have non existing slug')

    if not errors:
        console.print('No errors found', style="bold red")


def get_slugs_from_file(file_path):
    slugs = []

    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            slugs.append(row['slug'])

    return slugs


def aggregate_real_users():
    user_files = search_files(customers.get('user-filter'))
    aggregated_user_writer = get_writer(customers.get('aggregated-real-user-file'))
    aggregated_assignment_writer = get_writer(customers.get('aggregated-real-assignment-file'))

    user_headers = headers.get('users')
    assignment_headers = headers.get('assignments')

    user_group_id_enabled = customers.get('user-group-id-enabled')
    default_user_group_id = customers.get('default-user-group-id')

    if not user_group_id_enabled:
        user_headers.remove('groupId')

    aggregated_user_writer.writerow(user_headers)
    aggregated_assignment_writer.writerow(assignment_headers)

    console.print('Real users will be generated based on following files:', *user_files, sep='\n- ')

    for file_path in user_files:
        total_users = 0

        with open(file_path, newline='') as input_file:
            reader = csv.DictReader(input_file)

            for row in reader:
                row = sanitize_row(row)
                slug = map_field(row, 'users.slug')

                total_users += 1

                # TODO fix this workaround for BOM characters
                username = map_field(row, 'users.username') or row.get('\ufeffusername')

                user_data = [
                    username,
                    map_field(row, 'users.password'),
                ]

                if version == '1.x':
                    user_data.append(slug)

                if user_group_id_enabled:
                    user_data.append(map_field(row, 'users.groupId') or default_user_group_id)

                aggregated_user_writer.writerow(user_data)

                if version == '2.x':
                    aggregated_assignment_writer.writerow([
                        username,
                        slug
                    ])

            console.print(f'- Processed {file_path} - {total_users} users generated')


def check_duplicated_usernames(user_type):
    file_path = user_file_path(user_type)

    seen = {}
    duplicated_usernames = []

    with open(file_path, newline='') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            values = list(row.values())

            username = values[0]
            if username not in seen:
                seen[username] = 1
            else:
                if seen[username] == 1:
                    duplicated_usernames.append(username)
                seen[username] += 1

    if duplicated_usernames:
        for duplication in duplicated_usernames:
            console.print(duplication)
    else:
        console.print('No duplications were found.')


def user_file_path(user_type):
    paths = {
        "1.x": {
            selector.USER_TYPE_REAL: customers.get('aggregated-real-user-file'),
            selector.USER_TYPE_LQA_QA: customers.get('aggregated-user-file')
        },
        "2.x": {
            selector.USER_TYPE_REAL: customers.get('aggregated-real-assignment-file'),
            selector.USER_TYPE_LQA_QA: customers.get('aggregated-assignment-file')
        }
    }

    return paths.get(version).get(user_type)


def sanitize_row(row):
    row = {k: v.strip() for k, v in row.items()}

    return row


if __name__ == '__main__':
    customer = selector.customers()
    action = selector.actions()

    customers = config.get('customers').get(customer)
    version = customers.get('version')
    headers = config.get('headers').get(version)
    mappings = config.get('mappings').get(customer)

    if action == selector.CREATE_LINE_ITEMS:
        create_line_items()
    elif action == selector.CREATE_USERS:
        create_users()
    elif action == selector.CHECK_USER_SLUGS:
        user_type = selector.user_types()
        check_user_slugs(user_type)
    elif action == selector.AGGREGATE_REAL_USERS:
        aggregate_real_users()
    elif action == selector.CHECK_DUPLICATED_USERNAMES:
        user_type = selector.user_types()
        check_duplicated_usernames(user_type)
    else:
        console.print('Invalid operation')

from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator


CHECK_DUPLICATED_USERNAMES = 'check-duplicated-usernames'
CREATE_LINE_ITEMS = 'create-line-items'
CREATE_USERS = 'create-users'
AGGREGATE_REAL_USERS = 'aggregate-real-users'
CHECK_USER_SLUGS = 'check-user-slugs'
USER_TYPE_LQA_QA = 'qa-lqa'
USER_TYPE_REAL = 'real'

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


def customers():
    options = [
        {
            'type': 'list',
            'message': 'Select customer',
            'name': 'customer',
            'choices': [
                {
                    'name': 'Invalsi',
                    'value': 'invalsi'
                },
                {
                    'name': 'NSA',
                    'value': 'nsa'
                },
            ],
        }
    ]

    return prompt(options, style=style).get('customer')


def actions():
    options = [
        {
            'type': 'list',
            'message': 'Select action',
            'name': 'action',
            'choices': [
                Separator('=== Line Items ==='),
                {
                    'name': 'Create Line Items',
                    'value': CREATE_LINE_ITEMS
                },
                Separator('=== Users ==='),
                {
                    'name': 'Create Users',
                    'value': CREATE_USERS
                },
                {
                    'name': 'Aggregate Real Users',
                    'value': AGGREGATE_REAL_USERS
                },
                {
                    'name': 'Check User Slugs',
                    'value': CHECK_USER_SLUGS
                },
                {
                    'name': 'Check Duplicated Usernames',
                    'value': CHECK_DUPLICATED_USERNAMES
                },
            ],
        }
    ]

    return prompt(options, style=style).get('action')


def user_types():
    options = [
        {
            'type': 'list',
            'message': 'Select user type',
            'name': 'type',
            'choices': [
                {
                    'name': 'Real Users',
                    'value': USER_TYPE_REAL
                },
                {
                    'name': 'QA/LQA Users',
                    'value': USER_TYPE_LQA_QA
                },
            ],
        }
    ]

    return prompt(options, style=style).get('type')



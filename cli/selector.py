from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator

CHECK_DUPLICATED_USERNAMES = 'check-duplicated-usernames'
CREATE_LINE_ITEMS = 'create-line-items'
CREATE_USERS = 'create-users'
AGGREGATE_REAL_USERS = 'aggregate-real-users'
CHECK_USER_SLUGS = 'check-user-slugs'

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

customers = [
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

actions = [
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


def options():
    customer = prompt(customers, style=style)
    action = prompt(actions, style=style)

    return {**customer, **action}

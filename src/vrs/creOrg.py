headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

orgcreate_url = 'https://api.datadoghq.com/api/v1/org'
orgcreate_payload = {
    'name': '',
    'subscription': {
        'type': 'pro'
    },
    'billing': {
        'type': 'parent_billing'
    }
}

orglist = ''
org_names = []


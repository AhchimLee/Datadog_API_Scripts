headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

role_url = "https://api.datadoghq.com/api/v2/roles"

useradd_url = "https://api.datadoghq.com/api/v2/users"
useradd_payload = {
  'data': {
    'attributes': {
      'email': ''
    },
    'relationships': {
      'roles': {
        'data': [
          {
            'id': '',
            'type': 'roles'
          }
        ]
      }
    },
    'type': 'users'
  }
}

userinvite_url = "https://api.datadoghq.com/api/v2/user_invitations"
userinvite_payload = {
  'data': [
    {
      'relationships': {
        'user': {
          'data': {
            'id': '',
            'type': 'users'
          }
        }
      },
      'type': 'user_invitations'
    }
  ]
}

role_names_short = [ "Admin", "ReadOnly", "Standard", "DashboardReadOnly" ]

orglist = ''

org_name = ''

role_name = ''
role_name_short = ''
role_id = ''

emails = []
email_input_type = ''


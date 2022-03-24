headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

slack_integ_url = "https://api.datadoghq.com/api/v1/integration/slack"

slack_integ_payload = {
  "service_hooks": [
    {
      "account": "",
      "url": ""
    }
  ]
}

slack_account = ''

slack_integ_channel_url = 'https://api.datadoghq.com/api/v1/integration/slack/configuration/accounts/' + slack_account + '/channels'

slack_integ_channel_payload = {
  "display": {
    "message": True,
    "snapshot": True,
    "tags": False,
    "notified": False
  },
  "name": ""
}

orglist = ''
org_name = ''




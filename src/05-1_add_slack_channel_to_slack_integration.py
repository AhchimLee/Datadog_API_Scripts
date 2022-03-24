import os
import requests
import json
import re

from mods.decode import *

headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

slack_account = ''


slack_integ_channel_payload = {
  "display": {
    "message": True,
    "snapshot": True,
    "tags": False,
    "notified": False
  },
  "name": ""
}

## current orglist update=======================================================

user_id = '87bc7825-87b3-11eb-9857-da7ad0900002'
orglist_url = 'https://api.datadoghq.com/api/v2/users/' + user_id + '/orgs'
orglist_headers = headers = {'Content-Type': 'application/json', 'DD-API-KEY': api_key(), 'DD-APPLICATION-KEY': app_key() }

r = requests.get(orglist_url, headers=orglist_headers)

if not os.path.isdir("/datadog_api/status"):
    os.makedirs("/datadog_api/status")

if r.status_code == 200:
    orglist_infos = json.loads(r.text)
    orglist = "\n".join(sorted([ orglist_info['attributes']['name'] for orglist_info in orglist_infos['included'] if orglist_info['type'] == 'orgs' ]))
    orglist_output = open("/datadog_api/status/orglist.output", "w")
    orglist_output.write(orglist)
    orglist_output.close()

with open('/datadog_api/status/orglist.output', 'r') as f:
    data = f.read()
orglist = data.splitlines()

## =======================================================

org_name = ''

while True:
    org_name = input("Org 이름을 입력하세요: ")
    
    if not org_name:
        print("Org 이름이 입력되지 않았습니다.\n")
        continue
    elif not org_name in orglist:
        print("Org가 존재하지 않거나, 입력 시 오류가 발생하였습니다.")
        print("  1. /datadog_api/create_org/ 경로에" + org_name + ".output 파일이 존재하는지 확인 부탁드립니다.\n")
        #print("  2. 입력 시 ← 로 지우고 재작성하면 1. 번 결과가 옳더라도 오류가 발생합니다. 이 경우 다시 작성 부탁드립니다.\n")
        if os.path.isfile("/datadog_api/create_org/" + org_name + ".output"):
            print("해당 Org 이름이 구형입니다. Org 정보 업데이트가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE5팀 이아침)\n")
        continue
    elif (org_name in orglist) and (not os.path.isfile("/datadog_api/create_org/" + org_name + ".output")):
        print("해당 Org가 존재하지만, 유저를 추가하려면 API 관리 리스트에 추가가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE5팀 이아침)\n")
    else:
        print()
        break

org_out = open("/datadog_api/create_org/" + org_name + ".output", 'r')
org_info = json.loads(org_out.readline())
org_out.close()

headers['DD-API-KEY'] = org_info['api_key']['key']
headers['DD-APPLICATION-KEY'] = org_info['application_key']['hash']

#-------


#elif not re.match(r"^([A-Z0-9]+[-])*[A-Z0-9]+$", org_name):

while True:
    slack_account = input(org_name + " Org에 추가한 Slack Account 이름을 입력하세요. \n(DataDog > Slack Integration 화면 접속 시 저장되어 있는 Slack Account Name을 입력하시면 됩니다.) \n(ex. SREDataDogTEMP): ")
    if not slack_account:
        print("Slack Account Name이 입력되지 않았습니다.\n")
        continue
    else:
        break

slack_integ_channel_url = 'https://api.datadoghq.com/api/v1/integration/slack/configuration/accounts/' + slack_account + '/channels'

print()

while True:
    slack_integ_channel_payload['name'] = input("추가하고 싶은 Slack Channel 명을 입력하세요. \n(Slack Account 내에 채널이 존재해야 합니다.) \n(ex: #sre5-smb1): ")
    if not slack_integ_channel_payload['name']:
        print("Slack Channel Name이 입력되지 않았습니다.\n")
        continue
    else:
        if slack_integ_channel_payload['name'][0] != '#':
            slack_integ_channel_payload['name'] = '#' + slack_integ_channel_payload['name']
        break

print(slack_account + " 에 " + slack_integ_channel_payload['name'] + " Channel을 추가합니다.\n")

r = requests.post(slack_integ_channel_url, data=json.dumps(slack_integ_channel_payload), headers=headers)

if "errors" in r.text:
    print(slack_integ_channel_payload['name'] + " Channel은 추가되지 않았습니다.\n")
    print(r.text)
else:
    print(slack_integ_channel_payload['name'] + " Channel이 성공적으로 추가되었습니다.")
            
print()

print("exit() 을 입력하여 종료하세요.\n")


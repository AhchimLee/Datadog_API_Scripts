import os
import requests
import json
import re

from mods import decode,orgList
from vrs.addSlack import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()

    webhook_url_input()
    slack_account_name_input()
    slack_channel_name_input()

    slack_integ_add()
##=======================================================

def org_name_input():
    global org_name

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


def webhook_url_input():
    while True:
        slack_integ_payload['service_hooks'][0]['url'] = input("Webhook URL 을 입력하세요. \n(DataDog (Legacy) 앱이나 Webhook Integration 앱 추가로 Webhook URL 생성이 가능합니다. ) \n(ex. https://hooks.slack.com/services/~~): ")
        # (자세한 사항은 00_how_to_use.md 파일의 가이드 URL을 참고하세요.)
        if not slack_integ_payload['service_hooks'][0]['url']:
            print("Webhook URL이 입력되지 않았습니다.\n")
            continue
        else:
            break

    print()

def slack_account_name_input():
    global slack_integ_channel_url
    global slack_account

    while True:
        slack_integ_payload['service_hooks'][0]['account'] = slack_account = input(org_name + " Org에 추가할 Slack Account 이름을 입력하세요. \n(Slack Workspace 이름을 특수문자 없이 기입하세요.) \n(ex. SREDataDogTEMP): ")
        if not slack_account:
            print("Slack Account Name이 입력되지 않았습니다.\n")
            continue
        elif any(not c.isalnum() for c in slack_integ_payload['service_hooks'][0]['account']):
            print("\n특수문자 포함 시 에러가 발생합니다. 다시 입력 부탁드립니다.\n\n")
            continue
        else:
            break

    slack_integ_channel_url = 'https://api.datadoghq.com/api/v1/integration/slack/configuration/accounts/' + slack_account + '/channels'

    print()

def slack_channel_name_input():
    while True:
        slack_integ_channel_payload['name'] = input("Slack Channel 명을 입력하세요. \n(1. DataDog (Legacy) 앱의 URL일 시: Slack Account 내에 존재하는 Channel명을 기입하세요. )\n(2. Webhook Integration 앱의 URL일 시: Slack에서 Webhook Integration을 설치한 Slack Channel을 기입하세요.) \n(ex: #sre5-smb1): ")
        if not slack_integ_channel_payload['name']:
            print("Slack Channel Name이 입력되지 않았습니다.\n")
            continue
        else:
            if slack_integ_channel_payload['name'][0] != '#':
                slack_integ_channel_payload['name'] = '#' + slack_integ_channel_payload['name']
            break

def slack_integ_add():
    print("\n" + org_name + " 에 Slack: " + slack_account + " Account 를 연동하고 " + slack_integ_channel_payload['name'] + " Channel을 추가합니다.\n")
    
    slack_account_add()
    slack_channel_add()


def slack_account_add():
    r = requests.post(slack_integ_url, data=json.dumps(slack_integ_payload), headers=headers)

    if "errors" in r.text:
        print(slack_account + " Account는 추가되지 않았습니다.")
        print("스크립트를 종료합니다.\n")
        print(r.text)
        exit()
    else:
        print(slack_account + " Account가 성공적으로 추가되었습니다.")

    print()

def slack_channel_add():
    r = requests.post(slack_integ_channel_url, data=json.dumps(slack_integ_channel_payload), headers=headers)

    if "errors" in r.text:
        print(slack_integ_channel_payload['name'] + " Channel은 추가되지 않았습니다.\n")
        print(r.text)
    else:
        print(slack_integ_channel_payload['name'] + " Channel이 성공적으로 추가되었습니다.")

    print()

    print("exit() 을 입력하여 종료하세요.\n")


if __name__ == '__main__':
    main()


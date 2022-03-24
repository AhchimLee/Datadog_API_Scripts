import os
import requests
import json
import re

from mods import decode,orgList
from vrs.addUser import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    role_select()
    user_input()
    role_id_get()

    user_add_invite()
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
            print("  1. /datadog_api/create_org/ 경로에" + org_name + ".output 파일이 존재하는지 확인 부탁드립니다.")
            print("  2. 입력 시 ← 로 지우고 재작성하면 1. 번 결과가 옳더라도 오류가 발생합니다. 이 경우 다시 작성 부탁드립니다.\n")
            if os.path.isfile("/datadog_api/create_org/" + org_name + ".output"):
                print("해당 Org 이름이 구형입니다. Org 정보 업데이트가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE5팀 이아침)\n")
            continue
        elif (org_name in orglist) and (not os.path.isfile("/datadog_api/create_org/" + org_name + ".output")):
            print("해당 Org가 존재하지만, 유저를 추가하려면 API 관리 리스트에 추가가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE 8팀SK그룹파트 이아침)\n")
        else:
            print()
            break


def role_select():
    global role_name
    global role_name_short

    while True:
        print("1 Admin | 2 ReadOnly | 3 Standard | 4 Dashboard ReadOnly")
        role_name = input("윗 줄을 참고하여 적용할 권한을 입력하세요 (숫자 또는 권한명): ")

        if not role_name:
            print("권한이 입력되지 않았습니다.\n")
            continue
        elif role_name.replace(" ","") == '1' or role_name.replace(" ","") == 'Admin' or role_name.replace(" ","") == '1Admin':
            role_name_short = role_names_short[0]
            role_name = "Datadog Admin Role"
            print(role_name + " 권한이 선택되었습니다.\n")
            break
        elif role_name.replace(" ","") == '2' or role_name.replace(" ","") == 'ReadOnly' or role_name.replace(" ","") == '2ReadOnly':
            role_name_short = role_names_short[1]
            role_name = "Datadog Read Only Role"
            print(role_name + " 권한이 선택되었습니다.\n")
            break
        elif role_name.replace(" ","") == '3' or role_name.replace(" ","") == 'Standard' or role_name.replace(" ","") == '3Standard':
            role_name_short = role_names_short[2]
            role_name = "Datadog Standard Role"
            print(role_name + " 권한이 선택되었습니다.\n")
            break
        elif role_name.replace(" ","") == '4' or role_name.replace(" ","") == 'DashboardReadOnly' or role_name.replace(" ","") == '4DashboardReadOnly':
            role_name_short = role_names_short[3]
            role_name = "Dashboard Read Only Role"
            print(role_name + " 권한이 선택되었습니다.\n")
            break
        else:
            print("권한이 존재하지 않거나, 입력 시 오류가 발생하였습니다.")
            print("  1. Admin, ReadOnly, Standard, Dashboard ReadOnly 중 맞는 권한 또는 숫자를 입력했는지 다시 한번 확인 부탁드립니다.\n")
            continue


def user_input():
    global emails
    global email_input_type

    while True:
        print("1 한 줄: email1@email.com email2@email.com ...")
        print("2 한 개씩 여러번: email1@email.com 입력 후 엔터→ email2@email.com 입력 후 엔터→ ...")
        email_input_type = input("email을 한 줄로 입력하시겠습니까? 한 개씩 입력하시겠습니까? (1 or 2 입력): ")
        if email_input_type.replace(" ","") == '1' or email_input_type.replace(" ","") == '2':
            email_input_type = email_input_type.replace(" ","")
            print()
            break
        else:
            print("1 또는 2가 입력되지 않았습니다.\n")
            continue

    while email_input_type == '1':
        print("email1@email.com email2@email.com email3@email.com ...")
        emails = [email for email in input(org_name + "에 " + role_name + " 권한을 추가할 email을 위 형식과 같이 작성합니다: ").split()]
        if not emails:
            print("email이 입력되지 않았습니다.")
            continue
        else:
            if any(re.match(r"^((?!([A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+)).)*$", email) for email in emails):
                print("email 형식에 맞지 않거나, 입력 시 오류가 발생하였습니다.")
                print("  1. email 형식: (영문대소문자|숫자|.|+|_|- 1개 이상)@(영문대소문자|숫자|.|+|_|- 1개 이상).(영문대소문자 1개 이상)\n")
                for email in emails:
                    if re.match(r"^((?!([A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+)).)*$", email):
                        print("  " + email + "로 인해 오류가 발생하였습니다. 재 작성 부탁드립니다.")
                        print()
                continue
            else:
                print()
                break

    while email_input_type == '2':
        email = input(org_name + "에 " + role_name + " 권한을 추가할 email을 하나씩 입력하고 엔터합니다. (exit을 입력하여 종료): ")
        if email == 'exit':
            if not emails:
                print("email이 입력되지 않았습니다.")
                continue
            else:
                print()
                break
        elif not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", email):
            print("email 형식에 맞지 않거나, 입력 시 오류가 발생하였습니다.")
            print("  1. email 형식: (영문대소문자/숫자/./+/_/- 1개 이상)@(영문대소문자/숫자/./+/_/- 1개 이상).(영문대소문자 1개 이상)")
            print("  " + email + "은 저장되지 않았습니다.\n")
            continue
        else:
            emails.append(email)


def role_id_get():
    global role_id

    org_out = open("/datadog_api/create_org/" + org_name + ".output", 'r')
    org_info = json.loads(org_out.readline())
    org_out.close()

    headers['DD-API-KEY'] = org_info['api_key']['key']
    headers['DD-APPLICATION-KEY'] = org_info['application_key']['hash']

    r = requests.get(role_url, headers=headers)
    roles_output = open("/datadog_api/roles/" + org_name + ".output", "w")
    roles_output.write(r.text)
    roles_output.close()

    role_infos = json.loads(r.text)
    dashboard_readonly_flag = 0

    for role_info in role_infos['data']:
        if "Dashboard Read Only Role" == role_info['attributes']['name']:
            dashboard_readonly_flag = 1

    if role_name == "Dashboard Read Only Role":
        if dashboard_readonly_flag == 0:
            print("Dashboard ReadOnly Role 이 존재하지 않습니다. 관리자에게 문의해주세요. (SRE5팀 이아침)\n")
            exit()

    print("~~" + org_name + " Org의 권한 id 불러오기 완료~~\n")

    roles_out = open("/datadog_api/roles/" + org_name + ".output", 'r')
    roles_info = json.loads(roles_out.readline())['data']
    roles_out.close()

    roles = dict(zip([ role_n['attributes']['name'] for role_n in roles_info ], [ role_id['id'] for role_id in roles_info ]))

    role_id = roles[role_name]


def user_add_invite():
    print(emails)
    print("위 email 리스트를 " + org_name + "에 " + role_name + " 권한으로 추가합니다.\n")

    useradd_url = "https://api.datadoghq.com/api/v2/users"

    if not os.path.isdir("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/"): 
        os.makedirs("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/")
    if not os.path.isdir("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/invitation/"):
        os.makedirs("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/invitation/")

    for email in emails:
        ## user_add
        useradd_payload['data']['attributes']['email'] = email
        useradd_payload['data']['relationships']['roles']['data'][0]['id'] = role_id

        r = requests.post(useradd_url, data=json.dumps(useradd_payload), headers=headers)

        if not os.path.isfile("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/" + email + ".output"):
            useradd_output = open("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/" + email + ".output", "w")
            useradd_output.write(r.text)
            useradd_output.close()

            if "errors" in r.text:
                print(org_name + " Org에 " + email + " 유저는 추가되지 않았습니다. 다음 에러 메시지 확인 부탁드립니다.")
                print(r.text)
            else:
                print(org_name + " Org에 " + email + " 유저가 " + role_name + " 권한으로 추가되었습니다.")

        else:
            print(org_name + " Org에 " + email + " 유저 파일이 이미 생성되어 있습니다.")
            print("이전에 추가된 적이 있는지 확인 부탁드립니다.\n")

        print()

        ## user_send_invite
        useradd_out = open("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/" + email + ".output", 'r')
        useradd_info = json.loads(useradd_out.readline())

        email_id = useradd_info['data']['id']
        useradd_out.close()

        userinvite_payload['data'][0]['relationships']['user']['data']['id'] = email_id 

        r = requests.post(userinvite_url, data=json.dumps(userinvite_payload), headers=headers)
        
        if not os.path.isfile("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/invitation/" + email + ".output"):
            userinvite_output = open("/datadog_api/add_user/" + org_name + "/" + role_name_short + "/invitation/" + email + ".output", "w")
            userinvite_output.write(r.text)
            userinvite_output.close()

            if "errors" in r.text:
                print(org_name + " Org에 " + email + " 유저 초대 메일이 발송되지 않았습니다. 다음 에러 메시지 확인 부탁드립니다.")
                print(r.text)
            else:
                print(org_name + " Org에 " + email + " 유저 초대 메일이 발송되었습니다.")

        print()

    print("exit() 을 입력하여 종료하세요.\n")


if __name__ == '__main__':
    main()


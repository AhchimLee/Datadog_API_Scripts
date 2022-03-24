import requests
import json
import os
import re

from mods import decode,orgList
from vrs.chgOrg import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input_to_change()
    change_org_name()
##=======================================================


def org_name_input_to_change(): 
    while True:
        org_name = input("기존 Org 이름을 입력 후 엔터합니다: ")
        if org_name in org_names:
            print("기존 이름이 겹칩니다. ")
            while True:
                org_name = input("기존 이름을 다시 입력하세요: ")
                
                if org_name in org_names: 
                    print("기존 이름이 다시 겹칩니다.")
                    continue
                else:
                    break

        org_name_tobe = input("변경될 Org 이름을 입력 후 엔터합니다: ")
        if (org_name_tobe in org_names_tobe) or (org_name_tobe in orglist):
            print("변경될 이름이 기존 혹은 변경될 이름과 겹칩니다. ")
            while True:
                org_name_tobe = input("변경될 이름을 다시 입력하세요: ")
                
                if org_name_tobe in org_names_tobe: 
                    print("변경될 이름이 다시 겹칩니다.")
                    continue
                else:
                    break

        flag = input("계속 추가하시겠습니까? (y/n) (default: n): ")
        print()
        
        if not (flag.replace(" ","").lower() == 'y' or flag.replace(" ","").lower() == 'yes'):
            print(org_name + " → " + org_name_tobe + " 을 변경 리스트에 추가합니다.\n")
            org_names.append(org_name)
            org_names_tobe.append(org_name_tobe)

            if len(org_names) != len(org_names_tobe):
                print("기존 Org 이름 갯수와 변경될 Org 이름 갯수가 맞지 않습니다. 스크립트를 종료합니다.\n")
                exit()
            elif org_names and org_names_tobe:
                print()
                for i in range(len(org_names)): print(org_names[i] + " → " + org_names_tobe[i])
                is_replace = input("상기 내용대로 Org 이름 변경을 진행하시겠습니까? (y/n) (default: n): ")
            
                if is_replace.replace(" ","").lower() == 'y' or is_replace.replace(" ","").lower() == 'yes':
                    print("리스트 내용을 반영하여 Org  변경을 시작합니다.\n")
                    break
                else:
                    print('y가 입력되지 않아 스크립트를 종료합니다. 다시 실행 부탁드립니다. \n')
                    exit()
            else:
                print("기존 혹은 변경될 Org 이름이 입력되지 않았습니다.\n")
                exit()
        elif not os.path.isfile("/datadog_api/create_org/" + org_name + ".output"):
            print("해당 Org가 존재하지 않습니다.")
            if org_name in orglist:
                print("해당 Org는 API 관리 리스트에 추가가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE5팀 이아침)\n")
            continue
        elif not (org_name or org_name_tobe):
            print("기존 혹은 변경될 Org 이름이 입력되지 않았습니다.\n")
            continue
        elif not re.match(r"^([A-Z0-9]+[-])*[A-Z0-9]+$", org_name_tobe):
            print("변경될 이름이 Org 이름 형식에 맞지 않습니다. 다음과 같은 형식인지 확인 부탁드립니다.\n")
            print("ex1) 영문대문자 혹은 숫자 1개 이상")
            print("ex2) 영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상")
            print("ex3) 영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상")
            print("실제 예시: HYUNDAI-MOTORS-ZET IDPIA-INFRA3 S1-CLOUDMANAGER ... \n")
            continue

        print(org_name + " → " + org_name_tobe + " 을 변경 리스트에 추가합니다.\n")
        org_names.append(org_name)
        org_names_tobe.append(org_name_tobe)


def change_org_name():
    global orgreplace_url

    if len(org_names) != len(org_names_tobe):
        print("기존 Org 이름 갯수와 변경될 Org 이름 갯수가 맞지 않습니다. 스크립트를 종료합니다.\n")
        exit()
    elif org_names and org_names_tobe:
        for i in range(len(org_names)):
            org_out = open("/datadog_api/create_org/" + org_names[i] + ".output", 'r')
            org_info = json.loads(org_out.readline())
            org_out.close()
            
            orgreplace_url += org_info['org']['public_id']

            headers['DD-API-KEY'] = org_info['api_key']['key']
            headers['DD-APPLICATION-KEY'] = org_info['application_key']['hash']

            orgreplace_payload["name"] = org_names_tobe[i]

            org_info['org']['name'] = org_names_tobe[i]

            r = requests.put(orgreplace_url, data=json.dumps(orgreplace_payload), headers=headers)

            if "errors" in r.text:
                print(org_names[i] + " → " + org_names_tobe[i] + " Org는이름이 변경되지 않았습니다. 다음 에러 메시지를 확인해 주세요.")
                print(r.text)
            else:
                os.rename("/datadog_api/create_org/" + org_names[i] + ".output", "/datadog_api/create_org/" + org_names_tobe[i] + ".output")
                output = open("/datadog_api/create_org/" + org_names_tobe[i] + ".output", "w")
                output.write(json.dumps(org_info))
                output.close()

                print(org_names[i] + " → " + org_names_tobe[i] + " Org 이름 변경이 완료되었습니다.")
    else:
        print("입력된 Org 이름이 없습니다.\n")
        exit()

    print("\nexit() 을 입력하여 종료하세요.\n")



if __name__ == '__main__':
    main()

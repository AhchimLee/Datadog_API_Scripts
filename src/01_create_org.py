import requests
import json
import os
import re

from mods import decode,orgList
from vrs.creOrg import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    create_org()
##=======================================================


def org_name_input():
    while True:
        org_name = input("Org 이름을 1개씩 입력 후 엔터합니다. (exit을 엔터하여 입력받기 중지): ")
        if org_name == 'exit':
            if org_names:
                print()
                print(org_names)
                is_create = input("상기 리스트의 Org  생성을 진행하시겠습니까? (y/n) (default: n): ")
            
                if is_create.replace(" ","").lower() == 'y' or is_create.replace(" ","").lower() == 'yes':
                    print("리스트 내용을 반영하여 Org  생성을 시작합니다.\n")
                    break
                else:
                    print('y가 입력되지 않아 스크립트를 종료합니다. 다시 실행 부탁드립니다. \n')
                    exit()
            else:
                print("입력된 Org 이름이 없습니다.\n")
                exit()
        elif org_name in orglist:
            print('이미 생성된 Org가 있습니다.')
            print('/datadog_api/status/orglist.output 파일 참고 부탁드립니다.\n')
            if not os.path.isfile("/datadog_api/create_org/" + org_name + ".output"):
                print("해당 Org는 API 관리 리스트에 추가가 필요합니다. 관리자에게 문의 부탁드립니다. (현 관리자: SRE 8팀SK그룹파트 이아침)\n")
            continue
        elif not org_name:
            print('Org 이름이 입력되지 않았습니다.\n')
            continue
        elif not re.match(r"^([A-Z0-9]+[-])*[A-Z0-9]+$", org_name):
            print("Org 이름 형식에 맞지 않습니다. 다음과 같은 형식인지 확인 부탁드립니다.\n")
            print("ex1) 영문대문자 혹은 숫자 1개 이상")
            print("ex2) 영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상")
            print("ex3) 영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상-영문대문자 혹은 숫자 1개 이상")
            print("실제 예시: HYUNDAI-MOTORS-ZET IDPIA-INFRA3 S1-CLOUDMANAGER ... \n")
            continue
        print(org_name + " 을 생성 리스트에 추가합니다.\n")
        org_names.append(org_name)


def create_org():
    if org_names:
        for org_name in org_names:
            orgcreate_payload["name"] = org_name

            r = requests.post(orgcreate_url, data=json.dumps(orgcreate_payload), headers=headers)

            if not os.path.isfile("/datadog_api/create_org/" + org_name + ".output"):
                output = open("/datadog_api/create_org/" + org_name + ".output", "w")
                output.write(r.text)
                output.close()

            if "errors" in r.text:
                print(org_name + " Org는 추가되지 않았습니다. 다음 에러 메시지를 확인해 주세요.")
                print(r.text)
            else:
                print(org_name + " Org가 생성 완료되었습니다.")
    else:
        print("입력된 Org 이름이 없습니다.\n")
        exit()

    print("exit() 을 입력하여 종료하세요.\n")



if __name__ == '__main__':
    main()

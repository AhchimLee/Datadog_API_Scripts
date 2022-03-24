import os
import requests
import json
import re

from mods import decode,orgList
from vrs.addDash import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    dashboard_opt_select()

    dashboard_add()
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


def dashboard_opt_select():
    global dashboards_title
    global dashboards_types

    while True:
        print("\n1 AWS | 2 Azure")
        dashboard_type = input("클라우드 환경을 선택하세요 (숫자 입력): ")
        if dashboard_type.replace(" ","") == '1' or dashboard_type.replace(" ","").lower == 'aws':
            dashboards_types.append('AWS/')
            break
        elif dashboard_type.replace(" ","") == '2' or dashboard_type.replace(" ","").lower() == 'azure':
            dashboards_types.append('Azure/')
            print("스크립트를 종료합니다. \n")
            break
        else:
            print("정확한 값이 입력되지 않았습니다.\n")
            continue

    for dashboard_type in dashboards_types:
        dashboards_title.extend(os.listdir(dashboards_path + dashboard_type))

    if not dashboards_title:
        print("대시보드가 없습니다. 관리자에게 문의하세요. (SRE5팀 이아침)")
        exit()

def dashboard_add():
    for dashboard_title in dashboards_title:
        print(dashboard_title)
    print("\n상기 대시보드 리스트를 추가합니다.\n")

    for dashboard_type in dashboards_types:
        dashboards_title.sort()

        for dashboard_title in dashboards_title:
            dashboard_data = open(dashboards_path + dashboard_type + dashboard_title, 'r')
            dashboard = json.loads(dashboard_data.readline())
            dashboard_data.close()

            dashboard['title'] = dashboard['title'].replace('Default', org_name)

            r = requests.post(dashboard_url, data=json.dumps(dashboard), headers=headers)

            if "errors" in json.loads(r.text):
                print(dashboard_title + " dashboard는 추가되지 않았습니다. 아래 에러 메시지를 확인하세요.")
                print(r.text)
            else:
                print(dashboard_title + " dashboard가 성공적으로 추가되었습니다.")
                
    print("\nexit() 을 입력하여 종료하세요.\n")

if __name__ == '__main__':
    main()


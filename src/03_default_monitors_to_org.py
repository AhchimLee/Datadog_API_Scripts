import os
import requests
import json
import re

from mods import decode,orgList
from vrs.addMonitor import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    monitor_opt_select()

    monitor_add()
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

def monitor_opt_select():
    global monitor_input_type
    global monitor_types
    global monitors_title

    while True:
        monitor_input_type = input(org_name + " Org에 Default Monitor 리스트를 추가하시겠습니까? (y/n): ")
        if monitor_input_type.replace(" ","").lower() == 'y' or monitor_input_type.replace(" ","").lower() == 'yes':
            monitor_input_type = 'y'
            break
        elif monitor_input_type.replace(" ","").lower() == 'n' or monitor_input_type.replace(" ","").lower() == 'no':
            print("스크립트를 종료합니다. \n")
            exit()
        else:
            print("y 혹은 n이 입력되지 않았습니다.\n")
            continue

    while True:
        print("\n1 AWS | 2 Azure")
        monitor_type = input("Monitor 환경을 선택하세요 (숫자 입력): ")
        if monitor_type.replace(" ","") == '1' or monitor_type.replace(" ","").lower == 'aws':
            monitor_types.append('AWS/')
            break
        elif monitor_type.replace(" ","") == '2' or monitor_type.replace(" ","").lower() == 'azure':
            monitor_types.append('Azure/')
            print("스크립트를 종료합니다. \n")
            break
        else:
            print("정확한 값이 입력되지 않았습니다.\n")
            continue

    for monitor_type in monitor_types:
        monitors_title.extend(os.listdir(monitors_path + monitor_type))

    monitors_title.sort()

def monitor_add():
    if monitor_input_type == 'y':
        print()
        for monitor_title in monitors_title:
            print(monitor_title)
        print("\n상기 모니터 리스트를 추가합니다.\n")

        if not monitors_title:
            print("Monitor가 없습니다. 관리자에게 문의하세요. (SRE5팀 이아침)")
            exit()

    for monitor_type in monitor_types:
        monitor_titles = os.listdir(monitors_path + monitor_type)
        monitor_titles.sort()

        for monitor_title in monitor_titles:
            monitor_data = open(monitors_path + monitor_type + monitor_title, 'r')
            monitor = json.loads(monitor_data.readline())
            monitor_data.close()

            monitor['name'] = '[' + org_name + '] ' + monitor['name']

            r = requests.post(monitor_url, data=json.dumps(monitor), headers=headers)

            if monitor_type == 'synthetics/':
                monitor['options']['monitor_name'] = '[' + org_name + '] ' + monitor['options']['monitor_name']

                r = requests.post(synthetics_url, data=json.dumps(monitor), headers=headers)

            if "errors" in r.text:
                print(monitor_title + " monitor는 추가되지 않았습니다.")
                print('다음 에러 메시지를 확인해 주세요: \n' + r.text)
            else:
                print(monitor_title + " monitor가 성공적으로 추가되었습니다.")
                
    print("exit() 을 입력하여 종료하세요.\n")


if __name__ == '__main__':
    main()


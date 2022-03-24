import os
import requests
import json
import re

from mods import decode,orgList
from vrs.chgMonitorName import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    all_monitor_get()
    all_monitor_name_print()
    monitor_name_prefix_input()
    monitor_name_prefix_list()
    monitor_name_update_select()

    monitor_name_update()
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

def all_monitor_get():
    global all_monitor_list
    global all_synthetics_list

    r1 = requests.get(monitor_url, headers=headers)
    r2 = requests.get(synthetics_url, headers=headers)

    all_monitor_list = json.loads(r1.text)
    all_synthetics_list = json.loads(r2.text)['tests']

def all_monitor_name_print():
    print('-------------------')
    for monitor in all_monitor_list:
        print(monitor['name'])
        print('-------------------')
    for synthetic in all_synthetics_list:
        print(synthetic['name'])
        print('-------------------')

    print('▷ 전체 모니터 리스트입니다.\n')

def monitor_name_prefix_input():
    global monitor_prefix_name

    monitor_prefix_name = input('전체 모니터 이름에 추가할 말머리를 입력하세요 (ex. SKTELINK): ')
    monitor_prefix_name = '[' + monitor_prefix_name.replace(' ','') + ']'

def monitor_name_prefix_list():
    global monitors_info

    for monitor in all_monitor_list:
        if not monitor['type'] == 'synthetics alert':
            monitor_info = { 'id': monitor['id'], 'name': monitor_prefix_name + ' ' + monitor['name'], 'type': 'monitor' }

            if 'time given by NTP' not in monitor['message']:
                monitors_info.append(monitor_info)


    for synthetic in all_synthetics_list:
        public_id = synthetic['public_id']
        synthetic['name'] = synthetic['options']['monitor_name'] = monitor_prefix_name + ' ' + synthetic['name']

        if 'public_id' in synthetic: del(synthetic['public_id'])
        if 'monitor_id' in synthetic: del(synthetic['monitor_id'])
        if 'created_at' in synthetic: del(synthetic['created_at'])
        if 'modified_at' in synthetic: del(synthetic['modified_at'])
        if 'creator' in synthetic: del(synthetic['creator'])

        monitor_info = { 'id': public_id, 'name': synthetic['name'],  'type': synthetic['type'], 'payload': synthetic }

        monitors_info.append(monitor_info)


def monitor_name_update_select():
    global update_flag

    print('-------------------')
    for monitor_info in monitors_info:
        print(monitor_info['name'])
        print('-------------------')

    while True:
        update_flag = input('위와 같이 알람 이름 변경을 진행하시겠습니까? (y/n): ')

        if not update_flag:
            print('입력되지 않았습니다.')
            continue
        elif update_flag.replace(' ','').lower() == 'y' or update_flag.replace(' ','').lower() == 'yes':
            update_flag = 'y'
            break
        elif update_flag.replace(' ','').lower() == 'n' or update_flag.replace(' ','').lower() == 'no':
            print('알람 이름 변경을 진행하지 않습니다. 스크립트를 종료합니다.')
            exit()
        else:
            print('입력이 잘못되었습니다.')
            continue

    print()

def monitor_name_update():
    if update_flag == 'y':
        for monitor_info in monitors_info:

            if monitor_info['type'] == 'monitor':
                monitor_name_payload['name'] = monitor_info['name']

                r = requests.put(monitor_url + '/' + str(monitor_info['id']), data=json.dumps(monitor_name_payload), headers=headers)

            elif monitor_info['type'] == 'api':
                r = requests.put(synthetics_url + '/api/' + monitor_info['id'], data=json.dumps(monitor_info['payload']), headers=headers)

            elif monitor_info['type'] == 'browser':
                r = requests.put(synthetics_url + '/browser/' + monitor_info['id'], data=json.dumps(monitor_info['payload']), headers=headers)
     
            if "errors" in json.loads(r.text):
                print(monitor_info['name'] + " 알람 이름은 변경되지 않았습니다. \n다음 에러 메시지를 확인해 주세요.")
                print(r.text)
            else:
                print(monitor_info['name'] + " 알람 이름 변경 완료되었습니다.")

            print()

    print("exit() 을 입력하여 종료하세요.\n")


if __name__ == '__main__':
    main()


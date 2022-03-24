import os
import requests
import json
import re

from mods import decode,orgList
from vrs.manageNoti import *

##=======================================================
def main():
    global orglist

    headers['DD-API-KEY'] = decode.api_key()
    headers['DD-APPLICATION-KEY'] = decode.app_key()

    orglist=orgList.update()

    org_name_input()
    all_monitor_get()
    all_monitor_print()
    noti_work_select()
    noti_update_select()

    noti_update()
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
    global monitors_info

    r1 = requests.get(monitor_url, headers=headers)
    r2 = requests.get(synthetics_url, headers=headers)

    all_monitor_list = json.loads(r1.text)
    all_synthetics_list = json.loads(r2.text)['tests']

    for monitor in all_monitor_list:
        if not monitor['type'] == 'synthetics alert':
            message_split = monitor['message'].split('@', 1)
            monitor_info = {}

            monitor_info = { 'id': monitor['id'], 'name': monitor['name'], 'message_msg': message_split[0], 'message_rcv': '', 'type': 'monitor' }

            if 'time given by NTP' in message_split[0]:
                monitors_info
            elif len(message_split) < 2:
                monitors_info.append(monitor_info)
            else:
                if ' ' in message_split[1]:
                    monitor_info['message_rcv'] = '@' + ' '.join(message_split[1].split())
                else:
                    monitor_info['message_rcv'] = '@' + message_split[1]

                monitors_info.append(monitor_info)

    for synthetic in all_synthetics_list:
        message_split = synthetic['message'].split('@', 1)
        public_id = synthetic['public_id']

        if 'public_id' in synthetic: del(synthetic['public_id'])
        if 'monitor_id' in synthetic: del(synthetic['monitor_id'])
        if 'created_at' in synthetic: del(synthetic['created_at'])
        if 'modified_at' in synthetic: del(synthetic['modified_at'])
        if 'creator' in synthetic: del(synthetic['creator'])

        monitor_info = { 'id': public_id, 'name': synthetic['name'], 'message_msg': message_split[0], 'message_rcv': '', 'type': synthetic['type'], 'payload': synthetic }

        if len(message_split) < 2:
            monitors_info.append(monitor_info)
        else:
            if ' ' in message_split[1]:
                monitor_info['message_rcv'] = '@' + ' '.join(message_split[1].split())
            else:
                monitor_info['message_rcv'] = '@' + message_split[1]

            monitors_info.append(monitor_info)


def all_monitor_print():
    print('-------------------')
    for monitor_info in monitors_info:
        print(monitor_info['name'])
        print(monitor_info['message_rcv'])
        print('-------------------')

    print('▷ 전체 모니터 수신 리스트입니다.\n')


def noti_work_select():
    while True:
        print("1 알람 수신 추가 | 2 알람 수신 삭제 | 3 특정 알람 수신 변경 | 4 알람 수신 여러개 추가")
        noti_work = input("전체 모니터 대상으로 수행할 작업을 선택하세요. (숫자 입력): ")
        if noti_work.replace(" ","") == '1':
            noti_add()
            break
        elif noti_work.replace(" ","") == '2':
            noti_remove()
            break
        elif noti_work.replace(" ","") == '3':
            noti_change()
            break
        elif noti_work.replace(" ","") == '4':
            noti_add_many()
            break
        else:
            print("정확한 값이 입력되지 않았습니다.\n")
            continue


def noti_add():
    global noti_for_add

    while True:
        print('\nE-Mail: email@email.com ex) ahchim.lee@bespinglobal.com')
        print('Slack: slack-워크스페이스이름-채널이름 ex) slack-SREDataDogTEMP-sre5-smb1')
        print('Webhook: webhook-웹훅이름 ex) webhook-AlertNow')
        noti_for_add = input('위 형식처럼 전체 모니터에 추가할 알람을 기입해주세요: ')
        noti_for_add = noti_for_add.replace(' ','')

        if noti_for_add[0] == '@':
            noti_for_add = noti_for_add[1:]

        if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", noti_for_add):
            noti_for_add = '@' + noti_for_add
            break
        elif re.match(r"^slack([-][A-Za-z0-9]+)+$", noti_for_add):
            noti_for_add = '@' + noti_for_add
            break
        elif re.match(r"^webhook([-][A-Za-z0-9]+)+$", noti_for_add):
            noti_for_add = '@' + noti_for_add
            break
        else:
            print('형식에 맞지 않습니다. 다시 입력해주세요.')
            continue

    if noti_for_add:
        for i in range(len(monitors_info)):
            monitors_info_list = monitors_info[i]['message_rcv'].split()

            if not noti_for_add in monitors_info_list:
                monitors_info_list.append(noti_for_add)

            monitors_info[i]['message_rcv'] = ' '.join(monitors_info_list)


def noti_remove():
    global noti_for_remove

    while True:
        noti_for_remove = input('\n전체 모니터에서 제거할 알람을 기입해주세요: ')
        noti_for_remove = noti_for_remove.replace(' ','')

        if noti_for_remove[0] == '@':
            noti_for_remove = noti_for_remove[1:]

        if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", noti_for_remove):
            noti_for_remove = '@' + noti_for_remove
            break
        elif re.match(r"^slack([-][A-Za-z0-9]+)+$", noti_for_remove):
            noti_for_remove = '@' + noti_for_remove
            break
        elif re.match(r"^webhook([-][A-Za-z0-9]+)+$", noti_for_remove):
            noti_for_remove = '@' + noti_for_remove
            break
        else:
            noti_for_remove = '@' + noti_for_remove
            break

    if noti_for_remove:
        for i in range(len(monitors_info)):
            monitors_info_list = monitors_info[i]['message_rcv'].split()

            if noti_for_remove in monitors_info_list:
                monitors_info_list.remove(noti_for_remove)

            monitors_info[i]['message_rcv'] = ' '.join(monitors_info_list)

def noti_change():
    global noti_for_change_rm
    global noti_for_change_ad

    while True:
        print('\n\nE-Mail: email@email.com ex) ahchim.lee@bespinglobal.com')
        print('Slack: slack-워크스페이스이름-채널이름 ex) slack-SREDataDogTEMP-sre5-smb1')
        print('Webhook: webhook-웹훅이름 ex) webhook-AlertNow\n')
        
        noti_for_change_rm = input('전체 모니터에서 변경할 기존 알람을 기입해주세요: ')
        noti_for_change_ad = input('전체 모니터에 변경할 신규 알람을 기입해주세요: ')
        noti_for_change_rm = noti_for_change_rm.replace(' ','')
        noti_for_change_ad = noti_for_change_ad.replace(' ','')

        if noti_for_change_rm[0] == '@':
            noti_for_change_rm = noti_for_change_rm[1:]
        if noti_for_change_ad[0] == '@':
            noti_for_change_ad = noti_for_change_ad[1:]

        if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", noti_for_change_rm):
            noti_for_change_rm = '@' + noti_for_change_rm
            noti_for_change_ad = '@' + noti_for_change_ad
            break
        elif re.match(r"^slack([-][A-Za-z0-9]+)+$", noti_for_change_rm):
            noti_for_change_rm = '@' + noti_for_change_rm
            noti_for_change_ad = '@' + noti_for_change_ad
            break
        elif re.match(r"^webhook([-][A-Za-z0-9]+)+$", noti_for_change_rm):
            noti_for_change_rm = '@' + noti_for_change_rm
            noti_for_change_ad = '@' + noti_for_change_ad
            break
        else:
            print('형식에 맞지 않습니다. 다시 입력해주세요.')
            continue

    if noti_for_change_rm and noti_for_change_ad:
        for i in range(len(monitors_info)):
            monitors_info_list = monitors_info[i]['message_rcv'].split()

            if noti_for_change_rm in monitors_info_list:
                monitors_info_list.remove(noti_for_change_rm)

                if not noti_for_change_ad in monitors_info_list:
                    monitors_info_list.append(noti_for_change_ad)
                    #monitors_info_list.insert(1, noti_for_change_ad)

            monitors_info[i]['message_rcv'] = ' '.join(monitors_info_list)


def noti_add_many():
    global noti_for_add_list
    global noti_for_add_many

    while True:
        print('\nE-Mail: email@email.com ex) ahchim.lee@bespinglobal.com')
        print('Slack: slack-워크스페이스이름-채널이름 ex) slack-SREDataDogTEMP-sre5-smb1')
        print('Webhook: webhook-웹훅이름 ex) webhook-AlertNow')
        noti_for_add = input('위 형식처럼 전체 모니터에 추가할 알람을 공백\' \'으로 분리하여 기입해주세요: ')
        noti_for_add_list = noti_for_add.split()

        for noti_for_add in noti_for_add_list:
            if noti_for_add[0] == '@':
                noti_for_add = noti_for_add[1:]

            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", noti_for_add):
                noti_for_add = '@' + noti_for_add
            elif re.match(r"^slack([-][A-Za-z0-9]+)+$", noti_for_add):
                noti_for_add = '@' + noti_for_add
            elif re.match(r"^webhook([-][A-Za-z0-9]+)+$", noti_for_add):
                noti_for_add = '@' + noti_for_add
            
            noti_for_add_many = noti_for_add_many + noti_for_add + ' '

        if noti_for_add_many:
            break


    if noti_for_add_many:
        for i in range(len(monitors_info)):
            monitors_info_list = monitors_info[i]['message_rcv'].split()

            if not noti_for_add_list in monitors_info_list:
                monitors_info_list.append(noti_for_add_many)

            monitors_info[i]['message_rcv'] = ' '.join(monitors_info_list)

    print()

def noti_update_select():
    global update_flag

    all_monitor_print()

    while True:
        update_flag = input('위와 같이 알람 수신 변경을 진행하시겠습니까? (y/n): ')

        if not update_flag:
            print('입력되지 않았습니다.')
            continue
        elif update_flag.replace(' ','').lower() == 'y' or update_flag.replace(' ','').lower() == 'yes':
            update_flag = 'y'
            break
        elif update_flag.replace(' ','').lower() == 'n' or update_flag.replace(' ','').lower() == 'no':
            print('알람 수신 변경을 진행하지 않습니다. 스크립트를 종료합니다.')
            exit()
        else:
            print('입력이 잘못되었습니다.')
            continue

    print()

def noti_update():
    if update_flag == 'y':
        for monitor_info in monitors_info:
            if monitor_info['type'] == 'monitor':
                monitor_message_payload['message'] = monitor_info['message_msg'] + monitor_info['message_rcv']

                r = requests.put(monitor_url + '/' + str(monitor_info['id']), data=json.dumps(monitor_message_payload), headers=headers)
            elif monitor_info['type'] == 'api':
                monitor_info['payload']['message'] = monitor_info['message_msg'] + monitor_info['message_rcv']

                r = requests.put(synthetics_url + '/api/' + monitor_info['id'], data=json.dumps(monitor_info['payload']), headers=headers)
            elif monitor_info['type'] == 'browser':
                monitor_info['payload']['message'] = monitor_info['message_msg'] + monitor_info['message_rcv']

                r = requests.put(synthetics_url + '/browser/' + monitor_info['id'], data=json.dumps(monitor_info['payload']), headers=headers)
     
            if "errors" in json.loads(r.text):
                print(monitor_info['name'] + " 알람 수신은 변경되지 않았습니다. \n다음 에러 메시지를 확인해 주세요.")
                print(r.text)
            else:
                print(monitor_info['name'] + " 알람 수신 변경 완료되었습니다.")

            print()

    print("exit() 을 입력하여 종료하세요.\n")


if __name__ == '__main__':
    main()



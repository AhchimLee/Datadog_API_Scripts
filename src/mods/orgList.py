import requests
import json
import os
from operator import itemgetter

from .decode import *

user_id = '87bc7825-87b3-11eb-9857-da7ad0900002'
orglist_url = 'https://api.datadoghq.com/api/v2/users/' + user_id + '/orgs'
orglist_headers = headers = {'Content-Type': 'application/json', 'DD-API-KEY': api_key(), 'DD-APPLICATION-KEY': app_key() }

org_infos = []
org_filename = {}
orginfo_dir = "/datadog_api/status/"
orglist_dir = "/datadog_api/create_org/"

def new_list():
    global org_infos
    global org_filename

    r = requests.get(orglist_url, headers=orglist_headers)

    if not os.path.isdir(orginfo_dir):
        os.makedirs(orginfo_dir)

    if r.status_code == 200:
        orgs = json.loads(r.text)

        for old_name in os.listdir(orglist_dir):
            with open(os.path.join(orglist_dir, old_name), 'r+') as f:
                orgf = json.load(f)

                for org in orgs['included']:
                    if org['type'] == 'orgs':
                        org_info = {'name': org['attributes']['name'], 'id': org['attributes']['public_id']}

                        if org_info not in org_infos:
                            org_infos.append(org_info)

                        if org['attributes']['public_id']==orgf['org']['public_id']:
                            orgf['org']['name'] = org_filename[old_name.split('.')[0]] = org['attributes']['name'].replace('/', '')
                            f.seek(0)
                            json.dump(orgf, f)
                            f.truncate()
        
        org_infos = sorted(org_infos, key=itemgetter('name'))

        org_infos_output = open(os.path.join(orginfo_dir, 'org_infos.output'), 'w')
        org_infos_output.write(json.dumps(org_infos))
        org_infos_output.close()

    with open(os.path.join(orginfo_dir, 'org_infos.output'), 'r') as f:
        data = f.read()
    org_infos = json.loads(data)

def rename():
    #서버내 orglist 불러오고 이름동기화=====
    for oldn,newn in org_filename.items():
        if oldn!=newn:
            oldp=os.path.join(orglist_dir, oldn + '.output')
            newp=os.path.join(orglist_dir, newn + '.output')

            os.rename(oldp, newp)
    #=======================================

def delete():
    for old_name in os.listdir(orglist_dir):
        old_name = old_name.split('.')[0]
        if old_name not in list(org_filename.values()):
            if os.path.exists(os.path.join(orglist_dir, old_name + '.output')):
                os.remove(os.path.join(orglist_dir, old_name + '.output'))

def update():
    new_list()
    rename()
    delete()

    orglist = [org_info['name'] for org_info in org_infos]

    return orglist


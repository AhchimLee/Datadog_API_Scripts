headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

monitor_url = "https://api.datadoghq.com/api/v1/monitor"
synthetics_url = "https://api.datadoghq.com/api/v1/synthetics/tests"

monitor_message_payload = {
    'message': ''
}

orglist = ''
org_name = ''

all_monitor_list = []
all_synthetics_list = []
monitors_info = []

noti_for_add = ''
noti_for_remove = ''
noti_for_change_rm = ''
noti_for_change_ad = ''
noti_for_add_list = []
noti_for_add_many = ''

update_flag = ''


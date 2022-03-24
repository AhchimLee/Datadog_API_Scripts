headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

monitor_url = "https://api.datadoghq.com/api/v1/monitor"
synthetics_url = "https://api.datadoghq.com/api/v1/synthetics/tests"

monitor_name_payload = {
    'name': ''
}

orglist = ''
org_name = ''

all_monitor_list = []
all_synthetics_list = []
monitors_info = []

monitor_prefix_name = ''
update_flag = ''


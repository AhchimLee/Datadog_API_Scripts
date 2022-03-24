headers = {'Content-Type': 'application/json', 'DD-API-KEY': '', 'DD-APPLICATION-KEY': ''}

monitor_url = "https://api.datadoghq.com/api/v1/monitor"
synthetics_url = "https://api.datadoghq.com/api/v1/synthetics/tests/api"

monitor_payload = {}

org_name = ''

monitors_path = '/datadog_api/assets/monitors/'
monitors_title = []
monitor_types = ['default/', 'synthetics/']
monitor_input_type = ''


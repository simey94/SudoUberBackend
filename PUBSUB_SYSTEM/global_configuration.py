"""Configuration properties that are global"""

"""Load balancer stuff"""
runner = "python"
file_loadbalancer = "lb.py"

"""Main server stuff"""
s_location = "http://localhost:%s"
s_port = 8008
location = s_location % s_port
cat_port = 1237

hostname = "http://localhost:%s"
http_hostname = ""

publish_interval = 5
connection_threashold = 4

event_recovery_threashold = 60
event_recovery_sleep_time = 30

"""Response patterns"""
subscribe_return_pattern = {'response': {"subscriber_id": str}}
subscribe_arg_pattern = {'username': str, 'password': str}

poll_return_pattern = {'response': {"data": str}}
poll_arg_pattern = {'token': str, 'query': str}

accuracy = 1

SUCCESS_CODE = 0
ERROR_CODE = 1
REPETITION_CODE = 2
OUT_OF_ORDER_CODE = 3

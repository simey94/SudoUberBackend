"""Configuration for the server side of Saint Uber app"""


"""Load balancer stuff"""
runner = "python"
file_loadbalancer = "ilia_loadbalancer.py"
file_node = "node.py"

"""Main server stuff"""
s_location = "http://localhost:%s"
s_port = 8008
location = s_location % s_port

hostname = "http://localhost:%s"
http_hostname = ""


"""Response patterns"""
subscribe_return_pattern = {'response': {"subscriber_id": str}}
subscribe_arg_pattern = {'username': str, 'password': str}

poll_return_pattern = {'response': {"data": str}}
poll_arg_pattern = {'token': str, 'query': str}

SUCCESS_CODE = 0
ERROR_CODE = 1
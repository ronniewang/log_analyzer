import re
import time
import json
import os.path
import datetime


def yesterday_str():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')


start = time.time()
# pwd = '/Users/ronniewang'
pwd = os.path.dirname(os.path.realpath(__file__))
log_file_path = pwd + '/tomcat_kc_web_new_2.' + yesterday_str() + '.log'
out_file_path = pwd + '/out.log'
if not os.path.isfile(out_file_path):
    out_file = open(out_file_path, 'a+')
    line_num = 0
    with open(log_file_path) as log_file:
        for line in log_file:
            line_num += 1
            if line_num % 100000 == 0:
                print line_num
            match_obj = re.match(r'^.+\[requestId:(\d+)\]', line)
            if match_obj:
                match_api_uri = re.match(r'^.+\[(/[0-9a-zA-Z\./]+)[^\]]+\]', line)
                current_request_id = match_obj.group(1)

                if match_api_uri:
                    api = match_api_uri.group(1)
                    request_str = current_request_id, '|api|', api, '\n'
                    out_file.writelines(request_str)

                    # match_internal_uri = re.match(r'^.+(\[http://[^\]]+\])', line)
                    # if match_internal_uri:
                    #     pass
                    # internal_uri_str = current_request_id, ' internal uri: ', match_internal_uri.group(1), '\n'
                    # out_file.writelines(internal_uri_str)

                match_net_mills = re.match(r'^.+\[net send mills:(\d+)\]', line)
                if match_net_mills:
                    # pass
                    net_mills_str = current_request_id, '|net_mills|', match_net_mills.group(1), '\n'
                    out_file.writelines(net_mills_str)

                match_api_mills = re.match(r'^.+\[api mills:(\d+)\]', line)
                if match_api_mills:
                    api_mills = match_api_mills.group(1)
                    # pass
                    mills_str = current_request_id, '|api_mills|', match_api_mills.group(1), '\n'
                    out_file.writelines(mills_str)

request_map = {}
api_map = {}
request_count = 0
with open(out_file_path) as out_file:
    for line in out_file:
        request_count += 1
        request_statistic = {}
        req_items = line.split('|')
        request_id = req_items[0]
        if not request_map.has_key(request_id):
            request_map[request_id] = {'api': '', 'net_mills': 0, 'api_mills': 0}
        if req_items[1] == 'api':
            api = req_items[2].replace('\n', '')
            if not api_map.has_key(api):
                api_map[api] = 1
            else:
                api_map[api] += 1
            request_map[request_id]['api'] = req_items[2].replace('\n', '')
        if req_items[1] == 'net_mills':
            request_map[request_id]['net_mills'] += int(req_items[2])
        if req_items[1] == 'api_mills':
            request_map[request_id]['api_mills'] += int(req_items[2])
print json.dumps(request_map, indent=4)
print(request_count)
print(json.dumps(api_map, indent=4))

end = time.time()

print 'time elapsed is ', end - start, 'seconds'

import re
from datetime import datetime
import json

line_num = 0
pre_request_id = 0

start = datetime.now().microsecond

api_map = {}
api_num = 0

with open('/Users/ronniewang/tomcat_kc_web_new_2.2016-07-20.log') as log_file:
    for line in log_file:
        line_num += 1
        match_obj = re.match(r'^.+\[requestId:(\d+)\]', line)
        if match_obj:
            match_api_uri = re.match(r'^.+\[(/[0-9a-zA-Z\./]+)[^\]]+\]', line)
            current_request_id = match_obj.group(1)
            if current_request_id != pre_request_id:
                pre_request_id = current_request_id
                # print '====================================================='

            if match_api_uri:
                api = match_api_uri.group(1)
                api_statistic = {}
                if api_map.has_key(api):
                    api_statistic = api_map[api]

                if api_statistic.has_key('num'):
                    api_statistic['num'] += 1
                else:
                    api_statistic['num'] = 1
                api_map[api] = api_statistic
                print 'api: ', api, 'api num: ', api_statistic['num']
                # print 'request id:', current_request_id, 'api: ', api

            match_internal_uri = re.match(r'^.+(\[http://[^\]]+\])', line)
            if match_internal_uri:
                pass
                # print 'request id:', current_request_id, 'internal uri: ', match_internal_uri.group(1)

            match_net_mills = re.match(r'^.+\[net send mills:(\d+)\]', line)
            if match_net_mills:
                pass
                # print 'request id:', current_request_id, 'net mills: ', match_net_mills.group(1)

            match_api_mills = re.match(r'^.+\[api mills:(\d+)\]', line)
            if match_api_mills:
                pass
                # print 'request id:', current_request_id, 'api mills: ', match_api_mills.group(1)

end = datetime.now().microsecond

print 'time elapsed is ', (end - start) / 1000, 'seconds'

print json.dump(api_map, indent=4)


import re
import time
import os.path
import datetime
import send_email


class ApiStatistic:
    def __init__(self, api, total_api_num, total_mills, total_net_mills):
        self.api = api
        self.total_api_num = total_api_num
        self.total_mills = total_mills
        self.total_net_mills = total_net_mills

    def get_average_mills(self):
        return self.total_mills / self.total_api_num

    def get_average_net_mills(self):
        return self.total_net_mills / self.total_api_num


def yesterday_str():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')


start = time.time()
pwd = '/Users/ronniewang'
# pwd = os.path.dirname(os.path.realpath(__file__))
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
                    net_mills_str = current_request_id, '|net_mills|', match_net_mills.group(1), '\n'
                    out_file.writelines(net_mills_str)

                match_api_mills = re.match(r'^.+\[api mills:(\d+)\]', line)
                if match_api_mills:
                    api_mills = match_api_mills.group(1)
                    mills_str = current_request_id, '|api_mills|', match_api_mills.group(1), '\n'
                    out_file.writelines(mills_str)

request_map = {}
api_map = {}
request_count = 0
with open(out_file_path) as out_file:
    api = ''
    for line in out_file:
        request_count += 1
        req_items = line.split('|')
        request_id = req_items[0]
        if not request_map.has_key(request_id):
            request_map[request_id] = {'api': '', 'net_mills': 0, 'api_mills': 0}
        if req_items[1] == 'api':
            api = req_items[2].replace('\n', '')
            if not api_map.has_key(api):
                api_map[api] = {'num': 1, 'total_mills': 0, 'total_net_mills': 0}
            else:
                api_map[api]['num'] += 1
            request_map[request_id]['api'] = api
        if req_items[1] == 'net_mills':
            request_map[request_id]['net_mills'] += int(req_items[2])
            if api != '':
                api_map[api]['total_net_mills'] += int(req_items[2])
        if req_items[1] == 'api_mills':
            request_map[request_id]['api_mills'] += int(req_items[2])
            if api != '':
                api_map[api]['total_mills'] += request_map[request_id]['api_mills']
# print json.dumps(request_map, indent=4)
print 'total request: ', request_count
api_statistics = []
for k in api_map:
    if api_map[k]['num'] >= 10:
        api_statistics.append(
            ApiStatistic(k, api_map[k]['num'], api_map[k]['total_mills'], api_map[k]['total_net_mills']))

api_statistics = sorted(api_statistics, key=lambda x: x.total_api_num, reverse=True)

end = time.time()

message_list = ['statistic api num is: {}'.format(len(api_statistics))]
message_list.append('time elapsed is {}seconds').format(end - start)
for s in api_statistics:
    message_list.append(''.join([s.api.ljust(40), 'total num:', str(s.total_api_num).ljust(8), 'average mills:',
                                 str(s.get_average_mills()).ljust(5),
                                 '\taverage net mills:', str(s.get_average_net_mills()).ljust(5), '\n']))

print 'time elapsed is ', end - start, 'seconds'

print ''.join(message_list)
send_email.send("***@***.com", '***', ['ro_wsy@163.com'], ''.join(message_list))

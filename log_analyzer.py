# encoding: utf-8
import re
import time
import os.path
import datetime
import smtplib
import argparse

STATISTIC_API_CALL_NUM_THRESHOLD = 10

parser = argparse.ArgumentParser()
parser.add_argument("log_name", help="please provide a log_name to be statistic")
log_name = parser.parse_args().log_name

print log_name


def send(sender, password, receivers=[], message=''):
    try:
        mail_server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
        mail_server.login(sender, password)
        email = """From: {0}
To: {1}
Subject: {2}

{3}
""".format(sender, receivers, '【日志统计】' + yesterday, message)
        mail_server.sendmail(sender, receivers, email)
        print "Successfully sent email"
    except smtplib.SMTPException as e:
        print e
        print "Error: unable to send email"
    mail_server.quit()


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


extract_file_start = time.time()
pwd = '/Users/ronniewang'
# pwd = os.path.dirname(os.path.realpath(__file__))
yesterday = yesterday_str()
log_file_path = pwd + '/' + log_name + '.' + yesterday + '.log'
out_file_path = pwd + '/' + log_name + 'simple.log.' + yesterday

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
                current_request_id = match_obj.group(1)

                match_api_uri = re.match(r'^.+\[(/[0-9a-zA-Z\./]+)[^\]]+\]', line)
                if match_api_uri:
                    api = match_api_uri.group(1)
                    request_str = current_request_id, '|api|', api, '\n'
                    out_file.writelines(request_str)

                match_net_mills = re.match(r'^.+\[net send mills:(\d+)\]', line)
                if match_net_mills:
                    net_mills_str = current_request_id, '|net_mills|', match_net_mills.group(1), '\n'
                    out_file.writelines(net_mills_str)

                match_api_mills = re.match(r'^.+\[api mills:(\d+)\]', line)
                if match_api_mills:
                    api_mills = match_api_mills.group(1)
                    mills_str = current_request_id, '|api_mills|', match_api_mills.group(1), '\n'
                    out_file.writelines(mills_str)
extract_file_end = time.time()
print 'extract file time:%fs' % (extract_file_end - extract_file_start)

start = time.time()
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
            request_map[request_id]['api_mills'] = int(req_items[2])
            if api != '':
                api_map[api]['total_mills'] += request_map[request_id]['api_mills']

# print json.dumps(request_map, indent=4)
api_statistics = []
for k in api_map:
    if api_map[k]['num'] >= STATISTIC_API_CALL_NUM_THRESHOLD:
        api_statistics.append(
            ApiStatistic(k, api_map[k]['num'], api_map[k]['total_mills'], api_map[k]['total_net_mills']))

api_statistics = sorted(api_statistics, key=lambda x: x.total_mills / x.total_api_num, reverse=True)

end = time.time()

message_list = ['total request num: %d\n' % request_count, 'statistic api num: %d\n' % len(api_statistics),
                'analyzing time elapsed: %fs\n' % (end - start),
                '====================================================================================================\n']
for s in api_statistics:
    message_list.append(''.join([s.api.ljust(40), 'total num:', str(s.total_api_num).ljust(8), 'average mills:',
                                 str(s.get_average_mills()).ljust(8),
                                 'average net mills:', str(s.get_average_net_mills()).ljust(5), '\n']))

print ''.join(message_list)

import config

send(config.sender, config.password, config.receivers, ''.join(message_list))

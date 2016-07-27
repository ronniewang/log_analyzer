#!/usr/bin/env python
from os import listdir
import re

dir_name = '/opt/'
# dir_name = '/Users/ronniewang/dev/tools/'
files = [f for f in listdir(dir_name) if re.match('^tomcat.*', f)]

for file_name in files:
    print_line = [file_name.ljust(35)]
    with open(dir_name + file_name + '/conf/server.xml') as server_xml:
        for line in server_xml:
            server_port_match = re.match('\s*<Server port="(\d+)"', line)
            if server_port_match:
                print_line.append('server port: ' + server_port_match.group(1))

            connector_port_match = re.match('\s*<Connector port="(\d+)"', line)
            if connector_port_match:
                print_line.append(' connector port: ' + connector_port_match.group(1))

            redirect_port_match = re.match(r'\s*redirectPort="(\d+)"', line)
            if redirect_port_match:
                print_line.append(' redirect port: ' + redirect_port_match.group(1))

        print ''.join(print_line)

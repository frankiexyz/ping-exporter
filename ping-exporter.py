#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import sys
import subprocess
from urlparse import parse_qs, urlparse
import logging
import os
import re

def locate(file):
    #Find the path for fping
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
                return os.path.join(path, file)
    return "{}".format(file)

def ping(host, prot, interval, count, size, source):    
    filepath_cmd = [filepath]
    host_cmd = [host]
    # subnets are only supported for IPv4 due to the size of IPv6
    if '/' in host and prot == 4:
        # host = '-g {}'.format(host)
        host_cmd = ['-g', host]   
    
    source_cmd = []
    if source:
        source_cmd = ['-S', source]

    quiet_cmd = ['-q']
    version_cmd = ['-{}'.format(prot)]
    interval_cmd = ['-i', str(interval)]
    size_cmd = ['-b', str(size)]
    count_cmd = ['-c', str(count)]

    ping_command = filepath_cmd + version_cmd + quiet_cmd + size_cmd + count_cmd + host_cmd

    output = []    
    logger.info(ping_command)

    # Execute the ping
    p = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)       
    _, cmd_output = p.communicate()
    if p.returncode > 2:
        raise subprocess.CalledProcessError('oops')

    raw_outputs = cmd_output.split('\n')

    # Parse the fping output (tested on version 4.2)
    # example ping "8.8.8.8 : xmt/rcv/%loss = 10/10/0%, min/avg/max = 0.72/0.82/1.42"
    # example loss "192.1.1.1 : xmt/rcv/%loss = 10/0/100%"
    # https://www.debuggex.com/r/T5_Da8_kWGHpm8y1
    for ping in raw_outputs:
        match = re.search('(?P<ip_address>.*) :.*= \d+\/\d+\/(?P<loss>\d+)%(?:.*(?P<min>\d+\.?\d*)\/(?P<avg>\d+\.?\d*)\/(?P<max>\d+\.?\d*))?', ping)                
        if match is not None:       
            ip_address = match.group('ip_address').strip()
            loss = match.group('loss')
            if (loss != "100"):
                min_ms = match.group('min')
                avg_ms = match.group('avg')
                max_ms = match.group('max')
            else:
                min_ms = 0
                avg_ms = 0
                max_ms = 0        

            output.append("ping_avg_ms{{ip_address=\"{}\"}} {}".format(ip_address, avg_ms))
            output.append("ping_max_ms{{ip_address=\"{}\"}} {}".format(ip_address, max_ms))
            output.append("ping_min_ms{{ip_address=\"{}\"}} {}".format(ip_address, min_ms))
            output.append("ping_loss_percent{{ip_address=\"{}\"}} {}".format(ip_address, loss))

        else:
            ip_address = cmd_output.split(' :')[0]
            loss = 100
            min = 0
            avg = 0
            max = 0

    return output

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #Parse the url
        parsed_path = urlparse(self.path).query
        value = parse_qs(parsed_path)        
        # Retrieve the ping target

        if 'target' not in value:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('missing target')
            return

        address = value['target'][0]

        #Retrieve source address
        if "source" in value:
            source = value['source'][0]
        else:
            source = ''
        #Retrieve prot
        if "prot" in value:
            prot = value['prot'][0]
        else:
            prot = 4
        #Retrieve ping count
        if "count" in value:
            count = value['count'][0]
        else:
            count = 10
        #Retrieve ping packet size
        if "size" in value and int(value['size'][0]) < 10240:
            size = value['size'][0]
        else:
            size = 56
        #Retrieve ping interval
        if "interval" in value and int(value['interval'][0]) > 1:
            interval = value['interval'][0]
        else:
            interval = 25

        try:
            message = '\n'.join(ping(address, prot, interval, count, size, source))
        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('command error: {}'.format(e))        
            return

        #Prepare HTTP status code
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    #Locate the path of fping
    global filepath
    filepath = locate("fping")
    # filepath = '/usr/local/sbin/fping'
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    #Check if there is a special port configured
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    else:
        port = 8085
    logger.info('Starting server port {}, use <Ctrl-C> to stop'.format(port))
    server = ThreadedHTTPServer(('0.0.0.0', port), GetHandler)
    server.serve_forever()

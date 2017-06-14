#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import sys
import subprocess
from urlparse import parse_qs, urlparse

def ping(host, v6, count):
    if v6:
        ping_command = '/usr/bin/fping -6 -i 1 -p 500 -q -c {} {}'.format(count, host)
    else:
        ping_command = '/usr/bin/fping -4 -i 1 -p 500 -q -c {} {}'.format(count, host)
    output = []
    cmd_output = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    loss = cmd_output[1].split("%")[1].split("/")[2]
    min = cmd_output[1].split("=")[2].split("/")[0]
    avg = cmd_output[1].split("=")[2].split("/")[1]
    max = cmd_output[1].split("=")[2].split("/")[2].split("\n")[0]
    output.append("ping_avg {}".format(avg))
    output.append("ping_max {}".format(max))
    output.append("ping_min {}".format(min))
    output.append("ping_loss {}".format(loss))
    output.append('')
    return output

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).query
        value = parse_qs(parsed_path)
        address = value['target'][0]
        if "count" in value:
            count = value['count'][0]
        else:
            count = 10
        if "prot" not in value:
                message = '\n'.join(ping(address, False, count))
        elif value['prot'][0] == "4":
                message = '\n'.join(ping(address, False, count))
        elif value['prot'][0] == "6":
                message = '\n'.join(ping(address, True, count))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    else:
        port = 8085
    print 'Starting server port {}, use <Ctrl-C> to stop'.format(port)
    server = ThreadedHTTPServer(('0.0.0.0', port), GetHandler)
    server.serve_forever()

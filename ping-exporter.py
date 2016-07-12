#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import socket
import pyping
import urlparse
import pycurl
import cStringIO
import re
import ping

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def get_status_code(host):
        curl = pycurl.Curl()
        buff = cStringIO.StringIO()
        hdr = cStringIO.StringIO()
        curl.setopt(pycurl.URL, 'http://'+host+'/')
        curl.setopt(pycurl.WRITEFUNCTION, buff.write)
        curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
        curl.setopt(pycurl.HEADERFUNCTION, hdr.write)
        curl.perform()
        output=[]
        output.append("status_code "+str(curl.getinfo(pycurl.HTTP_CODE)))
        output.append('')
        return output

def ping_host(host):
	print "Ping to "+host
        if is_valid_ipv4_address(host):
                percent_lost, mrtt, artt=ping.quiet_ping(host,count=5)
        else:
                ip=socket.gethostbyname(host)
		print ip
                percent_lost, mrtt, artt=ping.quiet_ping(ip,count=5)
        output=[]
	print "AVG "+str(artt)
        output.append("ping_avg "+str(artt))
        output.append("ping_max "+str(mrtt))
        output.append("ping_loss "+str(percent_lost))
        output.append('')
        return output


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print parsed_path.query
        if "&" in parsed_path.query:
                domain=parsed_path.query.split('&')[1].split('=')[1]
                module=parsed_path.query.split('&')[0].split('=')[1]
                message = '\n'.join(get_status_code(domain))
        else:
                domain=parsed_path.query.split('=')[1]
                message = '\n'.join(ping_host(domain))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 9095), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()


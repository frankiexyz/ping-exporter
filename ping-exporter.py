i#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler
import socket
import pyping
import urlparse

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
class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        domain=parsed_path.query.split('=')[1]
        if is_valid_ipv4_address(domain):
                r=pyping.ping(domain,count=5)
        else:
                ip=socket.gethostbyname(domain)
                r=pyping.ping(ip,count=5)
        output=[]
        output.append("ping_avg "+r.avg_rtt)
        output.append("ping_max "+r.max_rtt)
        output.append("ping_min "+r.min_rtt)
        output.append("ping_loss "+str(r.packet_lost))
        output.append('')
        message = '\n'.join(output)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return



if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', 9095), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()

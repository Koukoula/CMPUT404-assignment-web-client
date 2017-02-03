#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        print code

class HTTPClient(object):
    def get_host_port(self,url):
        port = urlparse(url).port
        if port == None:
            port = 80
        return port

    def get_host_name(self,url):
        return urlparse(url).hostname

    def get_path(self,url):
        return urlparse(url).path

    def get_query(self,url):
        return urlparse(url).query

    def connect(self, host, port):
        # use sockets!
        clientSocket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host,port))
        return clientSocket

    def get_code(self, data):
        code = 500
        codeSplit = re.findall(r" (\d+) ", data)
        #print data
        if len(codeSplit) != 0:
            code = int(codeSplit[0])
        return code

    def get_headers(self,data):
        endString = '\r\n\r\n'
        endOfHeader = data.find(endString)
        return data[:endOfHeader+len(endString)]

    def get_body(self, data):
        endString = '\r\n\r\n'
        endOfHeader = data.find(endString)
        return data[endOfHeader+len(endString):]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        host = self.get_host_name(url)
        port = self.get_host_port(url)
        clientSocket = self.connect(host,port)
        path = self.get_path(url)
        query = self.get_query(url)
        if query != "":
            pq = path + '?' +query
        else:
            pq = path
        request = "GET " + pq + " HTTP/1.0\r\n"
        request += "Host: " + host + '\r\n'
        request += "Accept: */*\r\n"
        request += "\r\n"
        clientSocket.sendall(request)
        data = self.recvall(clientSocket)
        code = self.get_code(data)
        #header = self.get_headers(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host = self.get_host_name(url)
        port = self.get_host_port(url)
        clientSocket = self.connect(host,port)
        path = self.get_path(url)
        query = self.get_query(url)
        request = "POST " + path + " HTTP/1.0\r\n"
        request += "Host: " + host + '\r\n'
        request += "Accept: */*\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: " + str(len(query)) + '\r\n'
        request += "\r\n"
        if query != "":
            request += query
        request += '\r\n'
        clientSocket.sendall(request)
        data = self.recvall(clientSocket)
        code = self.get_code(data)
        #header = self.get_headers(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )

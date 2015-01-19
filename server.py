#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Neil Borle
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import os
import re
import SocketServer


def read_resource(path):
    """ Return the content of a resource.

    Data from the resource will be returned as a string. If the resource does
    not exist or cannot be opened, None is returned instead.

    :param path: path to the resource from the CWD.
    :type path: str

    :returns: str or None
    """
    try:
        with open(path) as fh:
            content = fh.read()
        return content
    except IOError:
        return None


class MyWebServer(SocketServer.BaseRequestHandler):

    """A simple webserver that handles GET requests."""

    def __init__(self, *args, **kwargs):
        self._baseurl = './www'
        self.headers = {'html': ('HTTP/1.1 200 OK\r\n'
                                 'Content-Type: text/html\r\n\r\n'),
                        'css': ('HTTP/1.1 200 OK\r\n'
                                'Content-Type: text/css\r\n\r\n')}
        return SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)

    def clean_path(self, path):
        """Clean path for security reasons.

        If the path has one or more leading '/..' strings, remove them.

        :param path: path to the resource from the CWD.
        :type path: str

        :returns: str
        """
        return re.sub(r'^\.?(\/\.\.)+', '', path)

    def get(self, data):
        """Handle a GET request with a response.

        This method extracts the path provided in the request, cleans it, and
        checks if it exists. If the resource is accessible it will be opened
        and sent back with an appropriate header.

        :param data: the content of the GET request
        :type data: str

        :returns: (str) an appropriate response

        """
        sub_path = self.clean_path(data.split(' ')[1])
        path = self._baseurl + sub_path
        if path.endswith('/'):
            path += 'index.html'
        elif os.path.isdir(path):
            return ('HTTP/1.1 302 Found\r\n'
                    'Location: http://127.0.0.1:8080%s/\r\n\r\n' % sub_path)

        resource_content = read_resource(path)
        if resource_content is None:
            return 'HTTP/1.1 404\r\n\r\n404 file not found'

        for content_type in self.headers:
            if path.endswith('.' + content_type):
                header = self.headers[content_type]
                return header + resource_content

    def handle(self):
        """Read in a request, handle it if it is a GET."""
        self.data = self.request.recv(1024).strip()
        operation = self.data.split(' ')[0]

        #print ("Got a request of: %s\n" % self.data)
        if operation in ['GET']:
            response = getattr(self, operation.lower())(self.data)
            self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

"""
    Copyright (C) 2008 Benjamin O'Steen

    This file is part of python-fedoracommons.

    python-fedoracommons is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    python-fedoracommons is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with python-fedoracommons.  If not, see <http://www.gnu.org/licenses/>.
"""

__license__ = 'GPL http://www.gnu.org/licenses/gpl.txt'
__author__ = "Benjamin O'Steen <bosteen@gmail.com>"
__version__ = '0.1'

import httplib2
#import urlparse
import urllib
import base64
import urllib2
from urllib2 import urlparse
import simplejson
from base64 import encodestring


from mimetypes import *

import mimetypes

from cStringIO import StringIO

class ConnectionError(Exception):
    def __str__(self):
        return "Connection failed"

class Connection:
    def __init__(self, base_url, username=None, password=None, path_cache=".cache"):
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        self.base_url = base_url
        self.response = None
        self.status = None
        self.username = username
        m = mimeTypes()
        self.mimetypes = m.getDictionary()

        self.url = urlparse.urlparse(base_url)

        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(base_url)

        self.scheme = scheme
        self.host = netloc
        self.path = path

        # Create Http class with support for Digest HTTP Authentication, if necessary
        self.h = httplib2.Http(path_cache)
        self.h.follow_all_redirects = True
        if username and password:
            self.h.add_credentials(username, password)

    def request_get(self, resource, args = None, headers={}):
        return self.request(resource, "get", args, headers=headers)

    def request_delete(self, resource, args = None, headers={}):
        return self.request(resource, "delete", args, headers=headers)

    def request_head(self, resource, args = None, headers={}):
        return self.request(resource, "head", args, headers=headers)

    def request_post(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "post", args , body = body, filename=filename, headers=headers)

    def request_put(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "put", args , body = body, filename=filename, headers=headers)

    def get_content_type(self, filename):
        extension = filename.split('.')[-1]
        guessed_mimetype = self.mimetypes.get(extension, mimetypes.guess_type(filename)[0])
        return guessed_mimetype or 'application/octet-stream'

    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'

        BOUNDARY = u'00hoYUXOnLD5RQ8SKGYVgLLt64jejnMwtO7q8XE1'
        CRLF = u'\r\n'

        if filename and body:
            #fn = open(filename ,'r')
            #chunks = fn.read()
            #fn.close()

            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)

            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type']='text/xml'
            headers['Content-Length'] = str(len(body))
        else:
            if headers.has_key('Content-Length'):
                del headers['Content-Length']

            headers['Content-Type']='text/plain'

            if args:
                if method == "get":
                    path += u"?" + urllib.urlencode(args)
                elif method == "put" or method == "post":
                    headers['Content-Type']='application/x-www-form-urlencoded'
                    body = urllib.urlencode(args)


        request_path = []
        # Normalise the / in the url path
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)

        resp, content = self.h.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(request_path)), method.upper(), body=body, headers=headers )
        # TODO trust the return encoding type in the decode?
        return {u'headers':resp, u'body':content.decode('UTF-8')}

    def save(self, metod, resource, args={}, body=None):
        """
        metod post or put
        """
        self.response = self.request(resource, metod, args=args, body=body)
        headers = self.response.get('headers')
        self.status = headers.get('status', headers.get('Status'))

        if self.status in ['200', 200, '201', 201]:
            return simplejson.loads(self.response.get('body').encode('UTF-8'))
        else:
            return False

    def delete(self, resource):
        """
        metod post or put
        """
        self.response = self.request_delete(resource)
        headers = self.response.get('headers')
        self.status = headers.get('status', headers.get('Status'))

        if self.status in ['200', 200, '204', 204]:
            return True
        else:
            return False

    def search(self, query, args={}, headers={'Accept':'text/json'}):
        """Low-level content box query - returns the message and response headers from the server.
           You may be looking for Store.search instead of this."""

        passed_args = {}
        passed_args.update(args)
        self.response = self.request(query, 'get', args=passed_args, headers=headers)
        headers = self.response.get('headers')
        self.status = headers.get('status', headers.get('Status'))

        if self.status in ['200', 200, '204', 204]:
            return simplejson.loads(self.response.get('body').encode('UTF-8'))
        else:
            return False


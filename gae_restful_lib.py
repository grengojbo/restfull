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

from google.appengine.api import urlfetch

import urlparse
from urllib import urlencode
import base64
from base64 import encodestring

from mimeTypes import *

import mimetypes

class GAE_Connection:
    def __init__(self, base_url):
        self.base_url = base_url
        m = mimeTypes()
        self.mimetypes = m.getDictionary()
        
        self.url = urlparse.urlparse(base_url)
        
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(base_url)

        self.scheme = scheme
        self.host = netloc
        self.path = path
    
    def request_get(self, resource, args = None, headers={}):
        return self.request(resource, urlfetch.GET, args, headers=headers)
        
    def request_delete(self, resource, args = None, headers={}):
        return self.request(resource, urlfetch.DELETE, args, headers=headers)
        
    def request_post(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, urlfetch.POST, args , body = body, filename=filename, headers=headers)
        
    def request_put(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, urlfetch.PUT, args , body = body, filename=filename, headers=headers)
        
    def request_head(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, urlfetch.HEAD, args , body = body, filename=filename, headers=headers)
        
    def get_content_type(self, filename):
        extension = filename.split('.')[-1]
        guessed_mimetype = self.mimetypes.get(extension, mimetypes.guess_type(filename)[0])
        return guessed_mimetype or 'application/octet-stream'
        
    def request(self, resource, method = urlfetch.GET, args = None, body = None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'
        
        if not headers.get('Content-Type', None):
            headers['Content-Type']='text/plain'
            
        request_path = []
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)
        full_path = u'/'.join(request_path)
        
        if args:
            full_path += u"?%s" % (urlencode(args))
        
        response = urlfetch.fetch(u"%s://%s%s" % (self.scheme, self.host, full_path), method=method, payload=body, headers=headers)
        
        r_headers={'status':response.status_code}
        r_headers.update(response.headers)
        
        return {u'headers':r_headers, u'body':response.content.decode('UTF-8')}

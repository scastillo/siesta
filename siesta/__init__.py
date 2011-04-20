#    Python Siesta
#
#    Copyright (c) 2008 Rafael Xavier de Souza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Siesta is a REST client for python
"""

#__all__ = ["API", "Resource"]
__version__ = "0.1"
__author__ = "Sebastian Castillo <castillobuiles@gmail.com>"
__contributors__ = []

import re
import urllib
import httplib
import logging

USER_AGENT = "Python-siesta/%s" % __version__


class Resource(object):
    # Attrs defined statically here and not computed by getattr
    STATIC_ATTRS = ('get', 'post', 'put', 'delete',)

    def __init__(self, uri, api):
        self.scheme, self.host, self.url, z1, z2 = httplib.urlsplit(uri)
        self.id = None
        self.conn = None
        self.headers = {'User-Agent': USER_AGENT}
        self.api = api

    def __getattr__(self, name):
        if name in self.STATIC_ATTRS:
            return super(Resource, self).__getattr__(name)
        # Inner resoruces for stuff like: GET /users/{id}/applications
        self.api.resources[name] = Resource(uri=self.api.base_url+'/'+self.url+'/'+name,
                                            api=self.api)
        return self.api.resources[name]


    def __call__(self, id=None):
        self.id = id
        return self
    
    # Set the "Accept" request header.
    # +info about request headers:
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
    def set_request_type(self, mime):
        if mime.lower() == 'json':
            mime='application/json'
        elif mime.lower() == 'xml':
            mime='application/xml'
        self.headers['Accept'] = mime

    # GET /resource
    # GET /resource/id?arg1=value1&...
    def get(self, **kwargs):
        if self.id == None:
            url = self.url
        else:
            url = self.url+'/'+str(self.id)
        if len(kwargs)>0:
            url = "%s?%s" % (url, urllib.urlencode(kwargs))
        print url
        self._request("GET", url)
        return self._getresponse()


    # POST /resource
    def post(self, **kwargs):
        data = urllib.urlencode(kwargs)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self._request("POST", self.url, data, headers)
        return self._getresponse()


    # PUT /resource/id
    def put(self, **kwargs):
        if not self.id:
            return
        url = self.url+'/'+str(self.id)
        data = urllib.urlencode(kwargs)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self._request("PUT", url, data, headers)
        return self._getresponse()


    # DELETE /resource/id
    def delete(self, id, **dargs):
        url = self.url+'/'+str(id)
        data = urllib.urlencode(dargs)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self._request("DELETE", url, data, headers)
        return self._getresponse()


    def _request(self, method, url, body=None, headers=None):
        if headers==None:
            headers={}
        if self.conn!=None:
            self.conn.close()

        if not headers.has_key('User-Agent'):
            headers['User-Agent'] = self.headers['User-Agent']
        if not headers.has_key('Accept') and self.headers.has_key('Accept'):
            headers['Accept'] = self.headers['Accept']

        if self.scheme == "http":
            self.conn = httplib.HTTPConnection(self.host)
        elif self.scheme == "https":
            self.conn = httplib.HTTPSConnection(self.host)
        else:
            raise IOError, "unsupported protocol: %s" % self.scheme

        self.conn.request(method, url, body, headers)

    def _getresponse(self):
        resp = self.conn.getresponse()
        if resp.status==200:
            m = re.match('^([^;]*); charset=(.*)$',
                        resp.getheader('content-type'))
            if m==None:
                mime, encoding = ('','')
            else:
                mime, encoding = m.groups()

            if mime == 'application/json':
                try:
                    import json
                except:
                    import simplejson as json
                ret = json.read(resp.read())

            elif mime == 'application/xml':
                print 'application/xml not supported yet!'
                ret = resp.read()

            else:
                ret = resp.read()
        else:
            ret = None

        resp.close()
        return ret


class API(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.resources = {}
        self.request_type = None

    def set_request_type(self, mime):
        self.request_type = mime
        # set_request_type for every instantiated resources:
        for resource in self.resources:
            self.resources[resource].set_request_type(mime)

    def __getattr__(self, name):
        if not name in self.resources:
            self.resources[name] = Resource(uri=self.base_url+'/'+name,
                                            api=self)
        return self.resources[name]

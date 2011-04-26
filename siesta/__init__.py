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
__version__ = "0.3"
__author__ = "Sebastian Castillo <castillobuiles@gmail.com>"
__contributors__ = []

import re
import urllib
import httplib
import logging
import simplejson as json

from urlparse import urlparse

USER_AGENT = "Python-siesta/%s" % __version__


class Resource(object):

    # TODO: some attrs could be on a inner meta class
    # so Resource can have a minimalist namespace  population
    # and minimize collitions with resource attributes
    def __init__(self, uri, api):
        logging.info("init.uri: %s" % uri)
        self.api = api
        self.uri = uri
        self.scheme, self.host, self.url, z1, z2 = httplib.urlsplit(self.api.base_url+'/'+self.uri)
        self.id = None
        self.conn = None
        self.headers = {'User-Agent': USER_AGENT}
        self.attrs = {}
        
    def __getattr__(self, name):
        """
        Resource attributes (eg: user.name) have priority
        over inner rerouces (eg: users(id=123).applications)
        """
        logging.info("getattr.name: %s" % name)
        # Reource attrs like: user.name
        if name in self.attrs:
            return self.attrs.get(name)
        logging.info("self.url: %s" % self.url)
        # Inner resoruces for stuff like: GET /users/{id}/applications
        key = self.uri+'/'+name
        self.api.resources[key] = Resource(uri=key,
                                           api=self.api)
        return self.api.resources[key]

    def __call__(self, id=None):
        logging.info("call.id: %s" % id)
        logging.info("call.self.url: %s" % self.url)
        if id == None:
            return self
        self.id = str(id)
        key = self.uri+'/'+self.id
        self.api.resources[key] = Resource(uri=key,
                                           api=self.api)
        return self.api.resources[key]
    
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

        logging.info(">>>>>>>>>>>>>>>>>>>method: %s" % method)
        logging.info(">>>>>>>>>>>>>>>>>>>url: %s" % url)
        logging.info(">>>>>>>>>>>>>>>>>>>headers: %s" % headers)
        logging.info(">>>>>>>>>>>>>>>>>>>body: %s" % body)
        self.conn.request(method, url, body, headers)

    def _getresponse(self):
        resp = self.conn.getresponse()
        logging.info("status: %s" % resp.status)
        logging.info("getheader: %s" % resp.getheader('content-type'))
        logging.info("read: %s" % resp.read())
        # TODO: Lets support redirects and more advanced responses
        # see: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        if resp.status in (200, 201, 202, 204, 205, 206):
            m = re.match('^([^;]*); charset=(.*)$',
                        resp.getheader('content-type'))
            if m==None:
                mime, encoding = ('','')
            else:
                mime, encoding = m.groups()

            if mime == 'application/json':
                ret = json.loads(resp.read())

            elif mime == 'application/xml':
                print 'application/xml not supported yet!'
                ret = resp.read()

            else:
                ret = resp.read()
        else:
            ret = None

        resp.close()

        if ret:
            self.attrs.update(ret)

        return self


class API(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.api_path = urlparse(base_url).path
        self.resources = {}
        self.request_type = None

    def set_request_type(self, mime):
        self.request_type = mime
        # set_request_type for every instantiated resources:
        for resource in self.resources:
            self.resources[resource].set_request_type(mime)

    def __getattr__(self, name):
        logging.info( "API.getattr.name: %s" % name)
        
        key = '/'+name
        if not key in self.resources:
            logging.info("Creating resource with uri: %s" % key)
            self.resources[key] = Resource(uri=key,
                                           api=self)
        return self.resources[key]

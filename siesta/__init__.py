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
__version__ = "0.4.1"
__author__ = "Sebastian Castillo <castillobuiles@gmail.com>"
__contributors__ = []

import re
import time
import urllib, urllib2
import httplib, httplib2
import logging
import simplejson as json

from urlparse import urlparse, urlsplit, parse_qsl

USER_AGENT = "Python-siesta/%s" % __version__


class Resource(object):

    # TODO: some attrs could be on a inner meta class
    # so Resource can have a minimalist namespace  population
    # and minimize collitions with resource attributes
    def __init__(self, uri, api):
        logging.info("init.uri: %s" % uri)
        self.api = api
        self.uri = uri
        self.scheme, self.host, self.url, z1, z2 = httplib.urlsplit(self.api.base_url + '/' + self.uri)
        self.id = None
        self.conn = None
        self.headers = {'User-Agent': USER_AGENT}
        self.attrs = {}
        self.response = None
        
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
        key = self.uri + '/' + name
        print key
        self.api.resources[key] = Resource(uri=key,
                                           api=self.api)
        self.api.resources[key].id = self.id
        return self.api.resources[key]

    def __call__(self, id=None):
        logging.info("call.id: %s" % id)
        logging.info("call.self.url: %s" % self.url)
        print "id: " + str(id)
        if id == None:
            return self
        print "id: " + str(id)
        self.id = str(id)
        key = self.uri + '/' + self.id
        print key
        self.api.resources[key] = Resource(uri=key,
                                           api=self.api)
        return self.api.resources[key]

    # Set the "Accept" request header.
    # +info about request headers:
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
    def set_request_type(self, mime):
        if mime.lower() == 'json':
            mime = 'application/json, text/javascript, */*; q=0.01'
        elif mime.lower() == 'xml':
            mime = 'application/xml'
        self.headers['Accept'] = mime
        
    # GET /resource
    # GET /resource/id?arg1=value1&...
    def get(self, query=None, **kwargs):
        print "entro al get: " + str(self.id)
        if self.id == None:
            url = self.url
        else:
            url = self.url + '/' + str(self.id)
#        params = kwargs
#        if mime != None:
#            self.set_request_type(mime)
        if query:
            if type(query).__name__ == 'dict':    
                if len(query) > 0:
                    url = "%s?%s" % (url, urllib.urlencode(query))
            else:
                raise TypeError('get params must to be dict')
        response, content = self._request("GET", url)
        return self._getresponse("GET", url, response, content)

    # POST /resource
    def post(self, **kwargs):
        data = kwargs
        meta = dict([(k, data.pop(k)) for k in data.keys() if k.startswith("__")])
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self._request("POST", self.url, data, headers, meta)
        return self._getresponse("POST", self.url, data, headers, meta)

    # PUT /resource/id
    def put(self, data=None,**kwargs):
        print "entro al put: " + str(self.id)
        if self.id == None:
            url = self.url
        else:
            url = self.url + '/' + str(self.id)
        #data = kwargs
        meta = dict([(k, data.pop(k)) for k in data.keys() if k.startswith("__")])
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        #self._request("PUT", url, data, headers, meta)
        
        response, content = self._request("PUT", url, data, headers, meta)        
        print response.status
        return self._getresponse("PUT", url, response, content, data, headers, meta)

    # DELETE /resource/id
    def delete(self, id, **kwargs):
        url = self.url + '/' + str(id)
        data = kwargs
        meta = dict([(k, data.pop(k)) for k in data.keys() if k.startswith("__")])
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self._request("DELETE", url, data, headers, meta)
        return self._getresponse("DELETE", url, data, headers, meta)

    def _request(self, method, url, body={}, headers={}, meta={}):
        if self.api.auth:
            headers.update(self.api.auth.make_headers())
        
        if self.conn != None:
            self.conn.close()

        if not 'User-Agent' in headers:
            headers['User-Agent'] = self.headers['User-Agent']
            
        if not 'Accept' in headers and 'Accept' in self.headers:
            headers['Accept'] = self.headers['Accept']
        
        if not 'Accept-Encoding' in headers and not 'Accept-Encoding' in self.headers:
             headers['Accept-Encoding'] = "gzip,deflate"

        if not 'Connection' in headers and not 'Connection' in self.headers:
            headers['Connection'] = "keep-alive"
        if not 'Accept-Charset' in headers and not 'Accept-Charset' in self.headers:
            headers['Accept-Charset'] = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
        
        if self.scheme == "http":
            #self.conn = httplib.HTTPConnection(self.host)
            self.conn = httplib2.Http()
        elif self.scheme == "https":
            #self.conn = httplib.HTTPSConnection(self.host)
            self.conn = httplib2.Http()
        else:
            raise IOError("unsupported protocol: %s" % self.scheme)

        body = urllib.urlencode(body)

        logging.info(">>>>>>>>>>>>>>>>>>>method: %s" % method)
        logging.info(">>>>>>>>>>>>>>>>>>>url: %s" % url)
        logging.info(">>>>>>>>>>>>>>>>>>>headers: %s" % headers)
        logging.info(">>>>>>>>>>>>>>>>>>>body: %s" % body)
        
        
        self.conn.follow_all_redirects = True
        #self.conn.request(method, url, body, headers)
        return self.conn.request(self.scheme + '://' + self.host + url, method=method, body=body, headers=headers, redirections=6)

    def _getresponse(self, method, url, response, content,body={}, headers={}, meta={}):
        #resp = self.conn.getresponse()
        #resp_status = resp.status
        #resp_body = resp.read()
        resp_status = response.status
        resp_body = content
        
        #logging.info("status: %s" % resp.status)
        logging.info("getheader: %s" % response['content-type'])
        logging.info("__read: %s" % resp_body)
        # TODO: Lets support redirects and more advanced responses
        # see: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

        # Handle 202 Accepted:
        #    Used to implement POST requests that take too long to complete:
        #
        #    On receiving a POST request the server creates a new resource,
        #    and returns status code 202(Accepted) with a representation of the new resource.
        #
        #    The purpose of this resource is to let the client
        #    track the status of the asynchronous task.
        #
        #    This resource representation includes the current status of the request
        #
        #    When the client submits a GET request to the task resource, do one of the following
        #    depending on the current status of the request:
        #     - Still processing
        #          Return response code 200 (OK)
        #          and a representation of the task resource with the current status.
        #     - On successful completion
        #          Return response code 303 (See Other)
        #          and a Location header containing a URI of a resource
        #          that shows the outcome of the task.
        #     - On task failure
        #          Return response code 200 (OK)
        #          with a representation of the task resource informing
        #          that the resource creation has failed.
        #          Client will need to read the body of the representation to find
        #          the reason for failure.

        #logging.info('status type: %s' % type(resp.status))
        if resp_status == 202:
            logging.info('Starting a 202 Accept polling process...')
            status_url = resp.getheader('content-location')
            if not status_url:
                raise Exception('Empty content-location from server')

            status_uri = urlparse(status_url).path
            status  = Resource(uri=status_uri, api=self.api).get()
            retries = 0
            MAX_RETRIES = 3
            resp_status = status.conn.getresponse().status
            logging.info("##########33>>>>>>>> status: %s" % resp_status)
            while resp_status != 303 and retries < MAX_RETRIES:
                logging.info('retry #%s' % retries)
                retries += 1
                status.get()
                time.sleep(5)
                
            if retries == MAX_RETRIES:
                raise Exception('Max retries limit reached without success')
            
            location = status.conn.getresponse().getheader('location')
            resource = Resource(uri=urlparse(location).path, api=self.api).get()
            return resource
        
        # Whit httplib2 and urllib2 is not necesary to handle 301 response
        # by default we follow 6 redirects
#        elif resp_status == 301:
#            logging.info('Starting a 301 Redirect process...')
#            location_url = resp.getheader('Location')
#            (scheme, netloc, path, query, fragment) = urlsplit(location_url)
#            params = {}
#            if query != '': 
#                params = parse_qsl(query)
#                params = dict(params)
#            print location_url
#            if not location_url:
#                raise Exception('Empty Location from server')
#
#            location_uri = urlparse(location_url).path
#            if location_uri ==  location_uri.replace(self.api.api_path, ''):
#                raise Exception('Api Base location change to ' + location_uri + ' and the api-base is ' + self.api.api_path)
#            location_uri =  location_uri.replace(self.api.api_path, '')
#
#            if len(params) > 0:
#                if method.lower() == 'get':
#                    resource  = Resource(uri=location_uri, api=self.api).get(params)
#                elif method.lower() == 'post':
#                    resource  = Resource(uri=location_uri, api=self.api).post(params)
#                elif method.lower() == 'put':
#                    resource  = Resource(uri=location_uri, api=self.api).put(params)
#                elif method.lower() == 'delete':
#                    resource  = Resource(uri=location_uri, api=self.api).delete(params)
#            else:
#                if method.lower() == 'get':
#                    resource  = Resource(uri=location_uri, api=self.api).get()
#                elif method.lower() == 'post':
#                    resource  = Resource(uri=location_uri, api=self.api).post()
#                elif method.lower() == 'put':
#                    resource  = Resource(uri=location_uri, api=self.api).put()
#                elif method.lower() == 'delete':
#                    resource  = Resource(uri=location_uri, api=self.api).delete()
#                else: 
#                    raise Exception                    
#            return resource            
        
        if resp_status in (200, 201, 202, 204, 205, 206):
            m = re.match('^([^;]*); charset=(.*)$',
                        response['content-type'])
            if m == None:
                mime, encoding = ('', '')
            else:
                mime, encoding = m.groups()

            if mime == 'application/json':
                ret = json.loads(resp_body)
                #This for is because some servers returne de json into " or ' and the firstime
                #of json.loads just creat a str
                for i in xrange(0,1):
                    if type(ret).__name__ != 'list' and type(ret).__name__ != 'dict':
                        ret = json.loads(ret)
                if type(ret).__name__ != 'list' and type(ret).__name__ != 'dict':
                    raise TypeError('The response content is not json is ' + type(ret).__name__)
            elif mime == 'application/xml':
                print 'application/xml not supported yet!'
                ret = resp_body

            else:
                ret = resp_body
        else:
            if resp_body:
                ret = resp_body
            else: 
                ret = None
        self.response = resp_status 
        #resp.close()

        if ret:
            self.attrs = ret
            # return self here and none otherwise?
        return self


class API(object):
    def __init__(self, base_url, auth=None):
        self.base_url = base_url
        self.api_path = urlparse(base_url).path
        self.resources = {}
        self.request_type = None
        self.auth = auth

    def set_request_type(self, mime):
        self.request_type = mime
        # set_request_type for every instantiated resources:
        for resource in self.resources:
            self.resources[resource].set_request_type(mime)

    def __getattr__(self, name):
        logging.info("API.getattr.name: %s" % name)
        
        key = '/' + name
        if not key in self.resources:
            logging.info("Creating resource with uri: %s" % key)
            self.resources[key] = Resource(uri=key,
                                           api=self)
        return self.resources[key]

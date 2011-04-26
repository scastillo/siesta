import logging
import simplejson as json

from mock import patch
from mock import Mock

from siesta import API
from siesta.tests import BaseTestCase


class TestSiesta(BaseTestCase):
    
    
    def setUp(self):
        self.getresponse_patcher = patch('httplib.HTTPConnection.getresponse')
        self.getresponse_mock = self.getresponse_patcher.start()

        self.response_patcher = patch('httplib.HTTPResponse')
        self.response_mock = self.response_patcher.start()
        
        self.response = self.response_mock.return_value
        self.response.status = 200
        self.response.getheader.return_value = "application/json; charset=UTF-8"
        
        self.getresponse_mock.return_value = self.response

        self.api = API("http://nuagehq.com/api/v1")

    def tearDown(self):
        self.getresponse_patcher.stop()
        self.response_patcher.stop()
        self.api.resources = {}
        
    def test_post(self):
        expected_response = json.dumps(dict(user='123',id='QWERTY123'))
        self.response.read.return_value = expected_response
        
        obj = self.api.obj.post(attr='value')
        logging.info(obj.headers)
        
        
    def test_siesta(self):
        expected_response = json.dumps(dict(user='123',id='QWERTY123'))
        self.response.read.return_value = expected_response
        
        
        sess = self.api.sessions().post(user='123')
        user1 = self.api.users(id=1)
        apps = self.api.users(id=1).applications(123)
        apps.get()
        logging.info(self.api.resources)
        logging.info(sess.url)
        logging.info(sess.headers)
        logging.info(sess.conn.getresponse())
        logging.info("session.user: %s" % sess.user)

        self.response.getheader.assert_called_with('content-type')
        self.assertEquals(expected_response, json.dumps(sess.attrs))

import logging
import simplejson as json

from mock import patch
from mock import Mock
from mock import sentinel

from siesta import API
from siesta.tests import BaseTestCase


class TestSiesta(BaseTestCase):
    def setUp(self):
        self.getresponse_patcher = patch('httplib.HTTPConnection.getresponse')
        self.getresponse_mock = self.getresponse_patcher.start()

        self.response_patcher = patch('httplib.HTTPResponse')
        self.response_mock = self.response_patcher.start()

        self.response = self.response_mock.return_value
        #self.response.status = 200
        self.response.getheader.return_value = "application/json; charset=UTF-8"

        self.getresponse_mock.return_value = self.response

        self.api = API("http://nuagehq.com/api/v1")

    def tearDown(self):
        self.getresponse_patcher.stop()
        self.response_patcher.stop()
        self.api.resources = {}

    def test_post(self):
        expected_response = json.dumps(dict(user='123', id='QWERTY123'))
        self.response.read.return_value = expected_response
        self.response.status = 200

        obj, resp = self.api.obj.post(attr='value')
        logging.info(obj.headers)
        logging.info("response: %s" % resp)
        #raise Exception()
        self.assertEqual(expected_response, json.dumps(obj.attrs))

    def test_put(self):
        expected_response = json.dumps(dict(user='123', id='QWERTY123'))
        self.response.read.return_value = expected_response
        self.response.status = 200
# lunes 730 
        obj = self.api.obj.put(attr='value')
        logging.info(obj)
        
    def test_delete(self):
        expected_response = json.dumps(dict(user='123', id='QWERTY123'))
        self.response.read.return_value = expected_response
        self.response.status = 200
        
        obj, resp = self.api.obj().delete(1)
        logging.info(obj)

    def test_202_accepted(self):
        # First accepted for start procesing, then response two time still processnig
        # finally a see other on complete.

        #response
        statuses = [202]

        def side_effect():
            return statuses.pop()

        statuses_mock = Mock()
        statuses_mock.side_effect = side_effect

        #FIXME fix the pop crazy behaviour
        class MyResponse(Mock):
            @property
            def status(_self):
                try:
                    return statuses.pop()
                except:
                    return 303
        response = MyResponse()
        self.getresponse_mock.return_value = response

        #getheader
        def getheader(header):
            headers = {
                'content-type': 'application/json; charset=UTF-8',
                'content-location': 'http://localhost/resource/123456/status',
                'location': 'http://localhost/resource/123456',
                }
            return headers.get(header, sentinel.DEFAULT) 
        response.getheader.side_effect = getheader

        #read
        expected_response = json.dumps(
            dict(
                state='pending',
                message='Your request has been accepted for processing.'
            )
        )
        response.read.return_value = expected_response

        obj, resp = self.api.collection.post(attr='value')
        logging.info(obj)

    def test_siesta(self):
        expected_response = json.dumps(dict(user='123', id='QWERTY123'))
        self.response.read.return_value = expected_response
        self.response.status = 200
        
        sess, resp = self.api.sessions().post(user='123')
        #user1 = self.api.users(id=1)
        apps = self.api.users(id=1).applications(123)
        apps.get()
        logging.info(self.api.resources)
        logging.info(sess.url)
        logging.info(sess.headers)
        logging.info(sess.conn.getresponse())
        logging.info("session.user: %s" % sess.user)

        self.response.getheader.assert_called_with('content-type')
        self.assertEquals(expected_response, json.dumps(sess.attrs))

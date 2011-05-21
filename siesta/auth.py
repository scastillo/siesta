class Auth(object):
    """Base class for specific auth schemes"""
    
    def encode_params(self, base_url, method, params):
        """Encodes params and adds more if needed for each auth scheme"""
        raise NotImplementedError()

    def make_headers(self):
        """Makes needed headers for each auth scheme"""


class APIKeyAuth(Auth):
    """
    Authentication using api_key and temporal token ala dynect
    """

    def __init__(self, api_key, auth_header_name="X-Authorization"):
        self.api_key = api_key
        self.auth_header_name = auth_header_name

    def encode_params(self):
        pass

    def make_headers(self):
        return {self.auth_header_name: self.api_key, }

Class BasicAuth(Auth):
    """
    Authentication using username and password
    """

    def __init__(self, api_username, api_password, auth_header_name="X-Authorization"):
        self.api_username = api_username
        self.api_password = api_password
        self.auth_header_name = auth_header_name
        
    def encode_params(self):
        basic_token = base64.encodestring('' + str(self.api_username) + ':' + str(self.api_password))
        basic_token = basic_token.replace('\n', '')
        return basic_token
    
    def make_headers(self):
        token = self.encode_params()
return {self.auth_header_name: 'Basic ' + token, }

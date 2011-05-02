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

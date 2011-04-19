#Python Siesta

The python REST client.

##Usage

    from siesta import RestClient
    api = RestClient('http://example.org')
    user = api.users(id='123').get(format='json')
    print "Hello %s!" % user.name


##Why a REST client when i got httplib, libcurl, urllib, etc..?



##Other REST clients for python

*   [*pylib*](http://example.com/)
*   [*python-rest-client*](http://example.com/)
*   [*pyrest*](http://example.com/)

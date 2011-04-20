#Python Siesta

The python REST client.

##Usage

Get the applications owned by the user 123:
(GET http://example.org/api/v1/users/123/applications)

    from siesta import API
    api = API('http://example.org/api/v1')
    user = api.users(123).applications.get()
    print "Hello %s!" % user.name


##Why a REST client when i got httplib, libcurl, urllib, etc..?



##Other REST clients for python

*   [*pylib*](http://example.com/)
*   [*python-rest-client*](http://example.com/)
*   [*pyrest*](http://example.com/)

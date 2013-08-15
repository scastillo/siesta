#Python Siesta

     from siesta import API
     api = API('http://myrestful/api/v1')

     # GET /resource
     api.resource.get()
     # GET /resource (with accept header = application/json)
     api.resource.get(format='json')
     # GET /resource?attr=value
     api.resource.get(attr=value)

     # POST /resource
     api.resource.post(attr=value, attr2=value2, ...)
     # GET /resource/id/resource_collection
     api.resoure(id).resource_collection().get()


##Other REST clients for python

*   pylib
*   [*python-rest-client*](https://code.google.com/p/python-rest-client/)
*   [*pyrest*](http://github.com/travisby/pyrest)

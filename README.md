# How to build a REST API in AppEngine with Python2.7 and Endpoints-proto-datastore.

## The project schema
```
project
├── app.yaml
├── main.py
└── endpoints_proto_datastore
```

Documentation [endpoints_proto_datastore](https://github.com/GoogleCloudPlatform/endpoints-proto-datastore), [Download zip](https://github.com/GoogleCloudPlatform/endpoints-proto-datastore/blob/zipfile-branch/endpoints_proto_datastore.zip?raw=true)

## Configuration

Google AppEngine needs app.yaml file to understand the project structure, paths and dependencies

```yaml
application: your_app_id
version: 1
runtime: python27
api_version: 1
threadsafe: true

handlers:
# Endpoints handler
- url: /_ah/spi/.*
  script: python_file.attribute

libraries:
- name: pycrypto
  version: latest
- name: endpoints
  version: 1.0
```


## Main file

First we need to `import` statements

```python
# google SDK endpoints
import endpoints
# ndb is A schemaless object datastore with automatic caching, a sophisticated query engine, and atomic transactions.
from google.appengine.ext import ndb
# module allows to make a handler
from protorpc import remote
# It will allow us to define one class
from endpoints_proto_datastore.ndb import EndpointsModel
```

### Creating objects

We need to define bussines object and data store object. If Endpoints-proto-datastore is used, there is no need to create 2 different classes, only one.
Endpoints-proto-datastore uses ndb for storing data in Google Cloud datastore.

```python
class Contact(EndpointsModel):
    """
    Contact model
    """
    _message_fields_schema = ('id', 'name', 'email', 'phone', 'country', 'favourite')
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    country = ndb.StringProperty()
    favourite = ndb.BooleanProperty()
```

I will create another class that contain a list of previous class to create a http method to POST a group of objects.
We can call one class within another using `ndb.StructuredProperty`.

```python
class ContactList(EndpointsModel):
    items= ndb.StructuredProperty(Contact, repeated=True)
```

### Creating the API class and methods.

The class must extend `remote.Service`.
The class must be decorated with `@endpoints.api`. This decorator has some params as `name`, `version` and `description` that AppEngine will use. 'name' must be lowercase.

```python
@endpoints.api(name="contacts",
               version="v1",
               description="API for contact management")
class ContactApi(remote.Service):

    @Contact.method(name="insertContact",
                    path="contact/insert")
    def insert_contact(self, contact):
        contact.put()
        return contact
```

Class methods will be define what is done after a http method is called. It needs a decorator `@<EndointsModel>.method` (a 'POST' method by default) or `@<EndointsModel>.query_method` ('GET' method by default). Both of them need parameters as:

* `name` - human readable name
* `path` - path to call the method
* `http_method` - 'POST', 'GET', 'PUT', 'DELETE'
* `request_fields` - tuple of fields
* `query_fields` - some parameters to extend the query as 'limit', 'pageToken' or 'order'

Finally we need to define which classes should build the API with a list of those classes.
Last line of file should be the assignment of `endpoint.api_server` to a variable defined in yaml file, in this case

```
script: main.APPLICATION
```

So this line should be as follows.

```python
APPLICATION = endpoints.api_server([ContactApi])
```

## Full Example

```python
"""Contact API implemented using Google Cloud Endpoints-proto-datastore.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""

import endpoints
from google.appengine.ext import ndb
from protorpc import remote  # module allows to make a handler
from endpoints_proto_datastore.ndb import EndpointsModel

class Contact(EndpointsModel):
    """
    Contact model
    """
    _message_fields_schema = ('id', 'name', 'email', 'phone', 'country', 'favourite')
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    country = ndb.StringProperty()
    favourite = ndb.BooleanProperty()

class ContactList(EndpointsModel):
    items= ndb.StructuredProperty(Contact, repeated=True)

@endpoints.api(name="contacts", version="v1", description="API for contact management")
class ContactApi(remote.Service):

    @Contact.method(name="insertContact",
                    path="contact/insert")
    def insert_contact(self, contact):
        contact.put()
        return contact

    @Contact.method(name="updateContact",
                    path="contact/update")
    def update_contact(self, contact):
        contact.put()
        return contact

    @Contact.method(request_fields=('id',),
                    name="deleteContact",
                    path="contact/delete/{id}",
                    http_method="DELETE")
    def delete_contact(self, contact):
        if not contact.from_datastore:
            raise endpoints.NotFoundException('Contact not found.')
        contact.key.delete()
        return contact

    @Contact.method(request_fields=('id',),
                    name="getContact",
                    path="contact/{id}",
                    http_method="GET")
    def get_contact(self, contact):
        if not contact.from_datastore:
            raise endpoints.NotFoundException('Contact not found.')
        return contact

    @Contact.query_method(name="listContacts",
                          path="contacts",
                          query_fields=('limit', 'pageToken'))
    def list_contacts(self, query):
        return query

    @ContactList.method(name="insertContacts",
                        path="contacts")
    def insert_contacts(self, contacts):
        for contact in contacts.items:
            if not contact.from_datastore:
                contact.put()
        return contacts

APPLICATION = endpoints.api_server([ContactApi])

```
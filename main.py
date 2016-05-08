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
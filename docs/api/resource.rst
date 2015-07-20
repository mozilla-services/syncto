##################
Resource endpoints
##################

.. _resource-endpoints:

In this section, the request example provided are performed using
`httpie <https://github.com/jkbr/httpie>`_ .


GET /history
============

**Requires authentication**

Returns all records of the current user for this resource.

The returned value is a JSON mapping containing:

- ``items``: the list of records, with exhaustive attributes

A ``Total-Records`` header is sent back to indicate the estimated
total number of records included in the response.

A header ``ETag`` will provide the current timestamp of the collection
(*see Server timestamps section*).  It is likely to be used by client
to provide ``If-Modified-Since`` or ``If-Unmodified-Since`` headers in
subsequent requests.

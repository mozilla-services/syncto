.. _resource-endpoints:

##################
Resource endpoints
##################

Get a list of records for a collection
======================================

**Requires authentication**

Returns all records of the current user for this collection.

Collection can be one of the
`Firefox Sync collections <https://docs.services.mozilla.com/storage/apis-1.5.html#collections>`_:

The default collections used by Firefox to store sync data are:

 - bookmarks
 - history
 - forms
 - prefs
 - tabs
 - passwords

The following additional collections are used for internal management
purposes by the storage client:

 - clients
 - crypto
 - keys
 - meta

The returned value is a JSON mapping containing:

- ``data``: the list of records, with exhaustive fields;

A ``Total-Records`` response header indicates the total number of records
in the collection.

A ``Last-Modified`` response header provides a human-readable (rounded
to second) version of the current collection timestamp.

For cache and concurrency control, an ``ETag`` response header gives the
value that consumers can provide in subsequent requests using ``If-Match``
and ``If-None-Match`` headers (see :ref:`the section about timestamps <server-timestamps>`).



.. http:get:: /buckets/syncto/collections/(collection_id)/records

    **Example request**:

    .. sourcecode:: http

        $ BID_AUDIENCE=https://token.services.mozilla.com/ BID_WITH_CLIENT_STATE=True \
            http GET https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records \
                --auth-type fxa-browserid --auth "user@email.com:P4S5W0RD" -v

        GET /v1/buckets/syncto/collections/history/records HTTP/1.1
        Authorization: BrowserID eyJhbGciOiJSUzI1NiJ9...FHGg
        Host: syncto.dev.mozaws.net
        User-Agent: HTTPie/0.9.2
        X-Client-State: 64e8bc35e90806f9a67c0ef8fef63...


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Access-Control-Expose-Headers: Content-Length, Quota-Remaining, Alert, \
            Retry-After, Last-Modified, Total-Records, ETag, Backoff, Next-Page
        Content-Length: 1680
        Content-Type: application/json; charset=UTF-8
        Date: Tue, 06 Oct 2015 13:57:24 GMT
        ETag: "1442849064460"
        Last-Modified: Mon, 21 Sep 2015 15:24:24 GMT
        Total-Records: 6

        {
            "data": [
                {
                    "id": "VLkOS7iT5C94",
                    "last_modified": 1441868927070,
                    "payload": "{\"ciphertext\":\"Wf2AoZiOly...\",\"IV\":\"jW7JFPf...\",\"hmac\":\"989352d9b5e0c6...\"}",
                    "sortindex": -1
                },
                {
                    "id": "qYYobAN_p9vS",
                    "last_modified": 1441868927070,
                    "payload": "{\"ciphertext\":\"3upjoLrO...7\",\"IV\":\"3O/nPq82xUT...\",\"hmac\":\"addce0f9d3024ed9fd0042b...\"}",
                    "sortindex": 100
                },
                ...
            ]
        }

    :statuscode 200: The request was processed.
    :statuscode 304: The collection did not change since value in ``If-None-Match`` header
    :statuscode 400: The request querystring is invalid
    :statuscode 401: Something went wrong with your authentication
    :statuscode 412: Collection changed since value in ``If-Match`` header



Filtering and Sorting
---------------------

Firefox Sync filtering options are exposed in syncto.

- ``_since`` with the ETag value to fetch changes from the previous
  time.
- ``_sort`` can be either ``newest``, ``oldest``, or ``index``
  (as well as ``-last_modified``, ``last_modified``, and ``-sortindex``).
- ``_limit`` to limit the number of items per pages (no limit by default).
- ``in_ids`` to define the list of requested records IDs.


Pagination
----------

The ``Next-Page`` header will be sent with the URL to fetch the next
page. It will include defined ``_limit`` and ``_token`` values
automatically.

When the ``Next-Page`` is not present, it means there is no more data
to fetch.


Counting
--------

Contrary to what Kinto does, the ``Total-Records`` only counts the
number of records contained in the current request
`for now <https://github.com/mozilla-services/syncto/issues/43>`_.

You may ask the request without the ``_limit`` parameter to get all
the records at once.


Polling for changes
-------------------

The ``_since`` parameter is provided as an alias for ``gt_last_modified``.
(Greater than ``last_modified``)

If the request header ``If-None-Match`` is provided as described in
the :ref:`section about timestamps <server-timestamps>` and if the
collection was not changed, a ``304 Not Modified`` response is returned.


Additionnal headers
-------------------

The ``Quota-Remaining`` header is not part of the Kinto protocol yet
but is passed through if present in Firefox Sync responses.

Its value is in Kilobyte (KB).


Get a collection record
=======================

**Requires authentication**

Returns a specific record by its id. The GET response body is a JSON mapping
containing:

- ``data``: the record with exhaustive schema fields;

IDs are kept between Firefox Sync and Syncto.

Firefox Sync IDs are generated on client side as 9 random Bytes
encoded in urlsafe base64 (``+`` and ``/`` are replaced with ``-`` and
``_``).

If the request header ``If-None-Match`` is provided, and if the record has not
changed meanwhile, a ``304 Not Modified`` is returned.


.. http:get:: /buckets/syncto/collections/(collection_id)/records/(record_id)

    **Example request**:

    .. sourcecode:: http

        $ http GET \
            https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS \
            Authorization:"BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ" \
            X-Client-State:64e8bc35e90806f9a67c0ef8fef63...

        GET /v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS HTTP/1.1
        Authorization: BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ
        Host: syncto.dev.mozaws.net
        User-Agent: HTTPie/0.9.2
        X-Client-State: 64e8bc35e90806f9a67c0ef8fef63...

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Access-Control-Expose-Headers: Content-Length, Alert, Retry-After, Last-Modified, ETag, Backoff
        Content-Length: 289
        Content-Type: application/json; charset=UTF-8
        Date: Tue, 06 Oct 2015 14:18:40 GMT
        ETag: "1441868927070"
        Last-Modified: Thu, 10 Sep 2015 07:08:47 GMT

        {
            "data": {
                "id": "d2X1O6-DyeFS",
                "last_modified": 1441868927070,
                "payload": "{\"ciphertext\":\"75IcW3P4WxUJipehWryevc+ygK5vojh3n...\",\"IV\":\"Sj3U2Nkk2IjE...\",\"hmac\":\"c6a530f348...b68b610351\"}",
                "sortindex": 2000
            }
        }

    :statuscode 200: The request was processed.
    :statuscode 304: The collection did not change since value in ``If-None-Match`` header
    :statuscode 401: Something went wrong with your authentication
    :statuscode 412: Collection changed since value in ``If-Match`` header


Delete a record
===============

**Requires authentication**

Delete a specific record by its id.

Note that contrary to what Kinto does, Firefox Sync count on clients to
create deleted records tombstones. Moreover Firefox Sync tombstones are
encrypted and look like real records for Syncto.

This endpoint should not be used to create tombstones but to remove
the record when the client decides that all clients already fetched
the tombstone.

By default this endpoint is deactivated and should be activated on a
per collection basis.


.. http:delete:: /buckets/syncto/collections/(collection_id)/records/(record_id)

    **Example request**:

    .. sourcecode:: http

        $ http DELETE \
            https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS \
            Authorization:"BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ" \
            X-Client-State:64e8bc35e90806f9a67c0ef8fef63...

        DELETE /v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS HTTP/1.1
        Authorization: BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ
        Host: syncto.dev.mozaws.net
        User-Agent: HTTPie/0.9.2
        X-Client-State: 64e8bc35e90806f9a67c0ef8fef63...

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Access-Control-Expose-Headers: Content-Length, Alert, Retry-After, Last-Modified, ETag, Backoff
        Content-Length: 0
        Date: Tue, 06 Oct 2015 14:18:40 GMT

    :statuscode 204: The record was deleted
    :statuscode 401: Something went wrong with your authentication
    :statuscode 405: This endpoint was not activated in the configuration
    :statuscode 412: Collection changed since value in ``If-Match`` header


Create or Update a record
=========================

**Requires authentication**

Create or replace a record with its id. The PUT body is a JSON mapping containing:

- ``data``: the values of the resource schema fields;

Because IDs are created on client side for Firefox Sync, this is the
only endpoint that you can use either to create new record or to
update them.

If you want to make sure that you don't erase an existing record when
creating one, you can use the ``If-None-Match: *`` header value.

The PUT response body is a JSON mapping containing:

- ``data``: the newly created/updated record, if all posted values are valid;

If the request header ``If-Match`` is provided, and if the record has
changed meanwhile, a ``412 Precondition failed`` error is returned.

There are no validation nor on the id format nor on the payload body.

By default this endpoint is deactivated and should be activated on a
per collection basis.

.. http:put:: /buckets/syncto/collections/(collection_id)/records/(record_id)

    **Example request**:

    .. sourcecode:: http

        $ echo '{
             "data": {
                 "payload": "{\"ciphertext\":\"75IcW3P4WxUJipehWryevc+ygK5vojh3nOadu7YSX9zJSm3eBHu5lNIg1UtDyt3b\",\"IV\":\"Sj3U2Nkk2IjE2S59hv0m7Q==\",\"hmac\":\"c6a530f3486142d1069f80bfaff907e0cc077a892cf7f9bd62f943b68b610351\"}", 
                 "sortindex": 2000
             }
         }' | http PUT \
            https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS \
            Authorization:"BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ" \
            X-Client-State:64e8bc35e90806f9a67c0ef8fef63...

        PUT /v1/buckets/syncto/collections/history/records/d2X1O6-DyeFS HTTP/1.1
        Authorization: BrowserID eyJhbGciOiJSUzI1NiJ9...i_dQ
        Content-Length: 275
        Content-Type: application/json
        Host: syncto.dev.mozaws.net
        User-Agent: HTTPie/0.9.2
        X-Client-State: 64e8bc35e90806f9a67c0ef8fef63...

        {
            "data": {
                "payload": "{\"ciphertext\":\"75IcW3P4WxUJipehWryevc+ygK5vojh3nOadu7YSX9zJSm3eBHu5lNIg1UtDyt3b\",\"IV\":\"Sj3U2Nkk2IjE2S59hv0m7Q==\",\"hmac\":\"c6a530f3486142d1069f80bfaff907e0cc077a892cf7f9bd62f943b68b610351\"}",
                "sortindex": 2000
            }
        }


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Access-Control-Expose-Headers: Content-Length, Alert, Retry-After, Last-Modified, ETag, Backoff
        Connection: keep-alive
        Content-Length: 289
        Content-Type: application/json; charset=UTF-8
        Date: Fri, 09 Oct 2015 10:04:13 GMT
        ETag: "1444385059190"
        Last-Modified: Fri, 09 Oct 2015 10:04:19 GMT

        {
            "data": {
                "id": "d2X1O6-DyeFS",
                "last_modified": 1444385059190,
                "payload": "{\"ciphertext\":\"75IcW3P4WxUJipehWryevc+ygK5vojh3nOadu7YSX9zJSm3eBHu5lNIg1UtDyt3b\",\"IV\":\"Sj3U2Nkk2IjE2S59hv0m7Q==\",\"hmac\":\"c6a530f3486142d1069f80bfaff907e0cc077a892cf7f9bd62f943b68b610351\"}",
                "sortindex": 2000
            }
        }


    :statuscode 200: The record was created or updated
    :statuscode 400: The request body is invalid
    :statuscode 401: Something went wrong with your authentication
    :statuscode 405: This endpoint was not activated in the configuration
    :statuscode 412: Collection changed since value in ``If-Match`` header

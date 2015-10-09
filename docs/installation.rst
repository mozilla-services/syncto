Installation
############


Run locally
===========

*Syncto* is based on top of the `cliquet <https://cliquet.readthedocs.org>`_
project, and as such, you may wanto to refer to
`cliquet's documentation <https://cliquet.readthedocs.org/>`_ for more details.


For development
---------------

By default, *Syncto* persists internal cache in Redis.

::

    git clone https://github.com/mozilla-services/syncto
    cd syncto
    make serve

:note:
   OSX users are warned that supplementary steps are needed to ensure proper
   installation of cryptographic dependencies is properly done; see
   :ref:`dedicated note <osx-install-warning>`.

If you already installed Syncto earlier and you want to recreate a
full environment (because of errors when running ``make serve``), please run::

    make maintainer-clean serve


Authentication
--------------

*Syncto* relies on Firefox Account BrowserID assertion to authenticate
users to the Token Server.

Note that you will need to pass through a BrowserID assertion with the
https://token.services.mozilla.com/ audience for Syncto to be able to
read Firefox Sync server credentials.

This can be made using `HTTPie <http://httpie.org/>`_ and
`PyFxA <https://pypi.python.org/pypi/PyFxA/>`_.

To install them:

.. code-block:: bash

    $ pip install httpie PyFxA

To build a Firefox Account Browser ID assertion for an existing user:

.. code-block:: http

    $ BID_AUDIENCE=https://token.services.mozilla.com/ \
        BID_WITH_CLIENT_STATE=True \
          http GET 'https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records'
            --auth-type fxa-browserid --auth "user@email.com:US3R_P4S5W0RD" -v


Once you have got a BrowserID Assertion, you can also reuse it to
benefit from Syncto cache features:

.. code-block:: http

    $ http GET 'https://syncto.dev.mozaws.net/v1/buckets/syncto/collections/history/records' \
        Authorization:"BrowserID eyJhbGciOiJSUzI1NiJ9..." \
        X-Client-State:64e8bc35e90806f9a67c0ef8fef63...


Cryptography libraries
======================

Linux
-----

On Debian / Ubuntu based systems::

    apt-get install libffi-dev libssl-dev

On RHEL-derivatives::

    apt-get install libffi-devel openssl-devel

OS X
----

Assuming `brew <http://brew.sh/>`_ is installed:

::

    brew install libffi openssl pkg-config

.. _osx-install-warning:

.. warning::

   Apple having dropped support for OpenSSL and moving to their own library
   recently, you have to force its usage to properly install cryptography-related
   dependencies::

       $ env LDFLAGS="-L$(brew --prefix openssl)/lib" \
             CFLAGS="-I$(brew --prefix openssl)/include" \
                 .venv/bin/pip install cryptography
       $ make serve


Running in production
=====================

.. _configuration:

Recommended settings
--------------------

Most default setting values in the application code base are suitable for production.

However, the set of settings mentionned below might deserve some review or adjustments:

.. code-block :: ini

    syncto.cache_backend = cliquet.cache.redis
    syncto.cache_url = redis://localhost:6379/1
    syncto.http_scheme = https
    syncto.http_host = <hostname>
    syncto.retry_after_seconds = 30
    syncto.batch_max_requests = 25
    syncto.cache_hmac_secret = <32 random bytes as hex>
    syncto.token_server_url = https://token.services.mozilla.com/

:note:

    For an exhaustive list of available settings and their default values,
    refer to `cliquet source code <https://github.com/mozilla-services/cliquet/blob/2.8.0/cliquet/__init__.py#L26-L83>`_.

     Click here for `Syncto specific settings <https://github.com/mozilla-services/syncto/blob/master/syncto/__init__.py#L20-L25>`_


Enable write access
-------------------

By default, collections are read-only. In order to enable write operations
on remote Sync collections, add some settings in the configuration with the
collection name:

.. code-block :: ini

    syncto.record_tabs_put_enabled = true
    syncto.record_tabs_delete_enabled = true
    syncto.record_passwords_put_enabled = true
    syncto.record_passwords_delete_enabled = true
    syncto.record_bookmarks_put_enabled = true
    syncto.record_bookmarks_delete_enabled = true
    syncto.record_history_put_enabled = true
    syncto.record_history_delete_enabled = true


Monitoring
----------

.. code-block :: ini

    # Heka
    syncto.logging_renderer = cliquet.logs.MozillaHekaRenderer

    # StatsD
    syncto.statsd_url = udp://carbon.server:8125

Application output should go to ``stdout``, and message format should have no
prefix string:


.. code-block :: ini

    [handler_console]
    class = StreamHandler
    args = (sys.stdout,)
    level = INFO
    formater = heka

    [formatter_heka]
    format = %(message)s


Adapt the logging configuration in order to plug Sentry:

.. code-block:: ini

    [loggers]
    keys = root, sentry

    [handlers]
    keys = console, sentry

    [formatters]
    keys = generic

    [logger_root]
    level = INFO
    handlers = console, sentry

    [logger_sentry]
    level = WARN
    handlers = console
    qualname = sentry.errors
    propagate = 0

    [handler_console]
    class = StreamHandler
    args = (sys.stdout,)
    level = INFO
    formater = heka

    [formatter_heka]
    format = %(message)s

    [handler_sentry]
    class = raven.handlers.logging.SentryHandler
    args = ('http://public:secret@example.com/1',)
    level = WARNING
    formatter = generic

    [formatter_generic]
    format = %(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %H:%M:%S


Running with uWsgi
------------------

To run the application using uWsgi, an **app.wsgi** file is provided.
This command can be used to run it::

    uwsgi --ini config/syncto.ini

uWsgi configuration can be tweaked in the ini file in the dedicated
**[uwsgi]** section.

Here's an example:

.. code-block :: ini

    [uwsgi]
    wsgi-file = app.wsgi
    enable-threads = true
    socket = /run/uwsgi/syncto.sock
    chmod-socket = 666
    cheaper-algo = busyness
    cheaper = 5
    cheaper-initial = 9
    workers = 14
    cheaper-step = 1
    cheaper-overload = 30
    cheaper-busyness-verbose = true
    master = true
    module = syncto
    harakiri = 120
    uid = ubuntu
    gid = ubuntu
    virtualenv = /data/venvs/syncto
    lazy = true
    lazy-apps = true
    single-interpreter = true
    buffer-size = 65535
    post-buffering = 65535

To use a different ini file, the ``SYNCTO_INI`` environment variable
should be present with a path set to it.
